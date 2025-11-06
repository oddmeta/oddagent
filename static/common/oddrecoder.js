
function convert(n) {
    var v = n < 0 ? n * 32768 : n * 32767;       // convert in range [-32768, 32767]
    return Math.max(-32768, Math.min(32768, v)); // clamp
}

class OddRecoder
{
    constructor() {
        this.mediaStream = null;        // 保存MediaStream对象
        this.audioChunks = [];          // 存储音频数据
        this.isRecording = false;       // 录音状态
        this.audioContext = null;
        this.audioSource = null;
        this.audioProcessor = null;
        this.chunkStride = 1024;
    }

    onClose(code, err) {
        console.log("close: ", code, err);
        this.isRecording = false;
        this.audioChunks = [];
        this.audioSource = null;
        this.audioProcessor = null;
        this.audioContext = null;
    }

    onError(code, err) {
        console.log("error: ", code, err);
        this.isRecording = false;
        this.audioChunks = [];
        this.audioSource = null;
        this.audioProcessor = null;
        this.audioContext = null;
    }

    startRecoder(onFeed = function(){}, onClose = function(){}, onError = function(){})
    {
        if (onClose != null)
            this.onClose = onClose;
        if (onError != null)
            this.onError = onError;

        navigator.getUserMedia = navigator.getUserMedia ||
        navigator.webkitGetUserMedia ||
        navigator.mozGetUserMedia;
        if (!navigator.getUserMedia) 
        {
            alert('不支持音频输入');
            return;
        }

        try {
            // 创建AudioContext，确保使用16000Hz采样率
            this.audioContext = new (window.AudioContext || window.webkitAudioContext)({sampleRate: 16000});
        } catch(e) {
            this.onError("createAudioContext", e.message);
            alert('创建AudioContext失败: ' + e.message);
            return;
        }
        // this.audioContext = new AudioContext({sampleRate:16000});
        this.audioSource = null;
        this.audioProcessor = null;
        this.audioChunks = []; // 清空之前的录音数据
        this.isRecording = true;

        navigator.getUserMedia({
            audio: { // 配置音频输入参数
                echoCancellation: true,
                noiseSuppression: true,
                autoGainControl: true,
                sampleRate: 16000
            }, 
            video: false // 禁用视频输入
        },function(stream) {
            this.mediaStream = stream; // 保存MediaStream对象
            this.audioSource = this.audioContext.createMediaStreamSource(stream); 
            this.audioProcessor = this.audioContext.createScriptProcessor(this.chunkStride,1,1);

            this.audioProcessor.onaudioprocess = function(e){
                var buffer = e.inputBuffer.getChannelData(0);
                var length = buffer.length;
                var i16array = new Int16Array(length);
                
                for(var i = 0; i < length; i++)
                {
                    // 确保转换正确，将[-1, 1]范围的音频数据转换为[-32768, 32767]范围的16位整数
                    i16array[i] = Math.max(-32768, Math.min(32767, Math.floor(buffer[i] * 32768)));
                }

                // 存储音频数据的副本，确保不直接引用处理中的数据
                this.audioChunks.push(new Int16Array(i16array));
                console.log("feed: ", i16array.length);
                
                // 只有在onFeed函数存在且明确返回非0值时才停止录音
                if (typeof onFeed === 'function') {
                    const result = onFeed((new Uint8Array(i16array.buffer)).buffer);
                    // 只有当result明确等于0时才不停止录音
                    if (result !== undefined && result !== null && result !== 0) {
                        this.stopRecoder();
                    }
                }
            }.bind(this)

            this.audioSource.connect(this.audioProcessor)
            this.audioProcessor.connect(this.audioContext.destination)
        }.bind(this),function(err){
            alert("open audio input failed")
            console.log("open audio input failed: ", err);
            this.isRecording = false;

            // this.state = ASR_CLIENT_EXCEPTION;
            // this.onError(CODE.ASR_ERROR_INTER, err);
            // this.onClose(CODE.ASR_ERROR_INTER, err);
        });
    }

    stopRecoder()
    {
        console.log("stop recorder: ", this.audioContext);
        this.isRecording = false;

        if(this.mediaStream != null) {
            try {
                this.mediaStream.getTracks().forEach(track => {
                    track.stop();
                });
            } catch(e) {
                console.error('停止MediaStream出错: ', e);
            }
            this.mediaStream = null;
        }

        if(this.audioProcessor != null)
        {
            try {
                this.audioSource.disconnect(this.audioProcessor);
                this.audioProcessor.disconnect(this.audioContext.destination);
            } catch(e) {
                console.error('断开音频连接出错: ', e);
            }
            this.audioProcessor = null;
        }

        if(this.audioContext != null) {
            try {
                this.audioContext.close();
            } catch(e) {
                console.error('关闭AudioContext出错: ', e);
            }
            this.audioContext = null;
        }

        // this.onClose(CODE.ASR_ERROR_INTER, err);
    }

    // 导出WAV文件的方法
    exportWav() {
        if (this.audioChunks.length === 0) {
            alert('没有录音数据可导出');
            return null;
        }

        try {
            // 合并所有录音数据
            let totalLength = 0;
            for (let i = 0; i < this.audioChunks.length; i++) {
                totalLength += this.audioChunks[i].length;
                console.log("totalLength: ", totalLength);
            }

            const data = new Int16Array(totalLength);
            let offset = 0;
            for (let i = 0; i < this.audioChunks.length; i++) {
                data.set(this.audioChunks[i], offset);
                offset += this.audioChunks[i].length;
            }

            // 创建WAV文件 - 使用标准格式
            const sampleRate = 16000; // 采样率
            const numChannels = 1; // 单声道
            const bytesPerSample = 2; // 16位
            const blockAlign = numChannels * bytesPerSample;
            const byteRate = sampleRate * blockAlign;
            const dataSize = totalLength * bytesPerSample;
            const buffer = new ArrayBuffer(44 + dataSize); // WAV文件头44字节
            const view = new DataView(buffer);

            // 写入WAV文件头 - 标准格式
            // RIFF chunk
            writeString(view, 0, 'RIFF');
            view.setUint32(4, 36 + dataSize, true);
            writeString(view, 8, 'WAVE');
            
            // fmt chunk
            writeString(view, 12, 'fmt ');
            view.setUint32(16, 16, true); // Subchunk1Size (16 for PCM)
            view.setUint16(20, 1, true); // AudioFormat (1 for PCM)
            view.setUint16(22, numChannels, true); // NumChannels
            view.setUint32(24, sampleRate, true); // SampleRate
            view.setUint32(28, byteRate, true); // ByteRate
            view.setUint16(32, blockAlign, true); // BlockAlign
            view.setUint16(34, 8 * bytesPerSample, true); // BitsPerSample
            
            // data chunk
            writeString(view, 36, 'data');
            view.setUint32(40, dataSize, true); // Subchunk2Size

            // 写入音频数据
            for (let i = 0; i < data.length; i++) {
                view.setInt16(44 + i * 2, data[i], true); // 小端格式
            }

            // 创建Blob并返回，使用标准MIME类型
            return new Blob([view], { type: 'audio/wav' });
        } catch (error) {
            console.error('导出WAV文件出错: ', error);
            alert('导出WAV文件失败: ' + error.message);
            return null;
        }
    }
}

// 辅助函数：写入字符串到DataView
function writeString(view, offset, string) {
    for (let i = 0; i < string.length; i++) {
        view.setUint8(offset + i, string.charCodeAt(i));
    }
}