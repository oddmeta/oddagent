

var ODDASR = function () {
    const ASR_CLIENT_INIT = 0;
    const ASR_CLIENT_CONNECTING = 1;
    const ASR_CLIENT_CONNECTED = 2;
    const ASR_CLIENT_SESSION_STARTING = 3;
    const ASR_CLIENT_SESSION_ESTABLISHED = 4;
    const ASR_CLIENT_SESSION_STOPING = 5;
    const ASR_CLIENT_SESSION_STOPED = 6;
    const ASR_CLIENT_DESTORYING = 7
    const ASR_CLIENT_DESTORYED = 8;
    const ASR_CLIENT_EXCEPTION = 9;
    const ASR_CLIENT_CLOSED = 10;     

    const EM_MAI_OPENSDK_CREATE_ENGINE_ERROR = 20040007
    const EM_MAI_JDLSERVER_ASR_ID_NOVALID = 10040006


    //http to do next.
    const ASR_MODULE_NAME = "oddasr";
    const ASR_MODULE_VERSION = "v1.0.2";

    /**
     * OddAsr API接口调用返回值或回调状态.
     * @readonly
     * @global
     * @enum {number}
     */
    const CODE = {
        /** 操作成功 */
        ASR_ERROR_NONE:0,
        /** 参数出错 */
        ASR_ERROR_ARGS:-1,
        /** 网络错误 */
        ASR_ERROR_NET:-2,
        /** 会话token验证重复 */
        ASR_ERROR_SESSION_DUP:-3,// abort
        /** 会话token验证识别 */
        ASR_ERROR_TOKEN:-4,     // abort
        /** 识别对象逻辑装错误 */
        ASR_ERROR_STATE:-5,
        /** 内部错误 */
        ASR_ERROR_INTER:-6,
        /** 资源不足 */
        ASR_ERROR_NO_RESOURCE:-7,
        /** 引擎创建错误 */
        ASR_ERROR_ENIGNE:-8,
        /** ASR ID非法 */
        ASR_ID_NO_VALID:-9,
        /** ASRSERVER 内部链路 */
        ASR_ERROR_ASRSERVER:-10
    };


    /**
     * `onLog` 日志回调函数.
     *
     * @callback onLog
     * @param {string} module   -   模块名字
     * @param {string} content  -   日志内容 
     */

    /**
     * `onWarning` 警告消息回调函数
     *
     * @callback onWarning
     * @param {int} warningType     -   警告类型
     * @param {string} content      -   警告内容
     */

    /**
     * `onError` 错误消息回调函数
     *
     * @callback onError
     * @param {CODE} errorType      -   错误类型
     * @param {string} content      -   错误描述
     */

    /**
     * `onRelease` 调用OddAsr.destroyAsrClient(),产生释放{@link ODDASRCli}回调
     *
     * @callback onRelease
     * @param {CODE} errorType     -    错误类型 
     */

    /**
     * `onStart` 调用{@link ODDASRCli}.start()后,产生的回调
     *
     * @callback onStart
     * @param {CODE} errorType     -    错误类型 
     */


    /**
     * `onStop` 调用{@link ODDASRCli}.stop()后,产生的回调
     *
     * @callback onStop
     * @param {CODE} errorType     -    错误类型 
     */

    /**
     * `onRecogResult` 识别到文本结果后,产生的回调
     *
     * @callback onRecogResult
     * @param {object} result       -       识别结果
     * @param {int} result.bgTime   -       开始时间(单位:ms)
     * @param {int} result.edTime   -       结束时间(单位:ms)
     * @param {int} result.fin      -       文本标志(0:临时结果,1:最终结果)
     * @param {string} result.text  -       文本内容
     */




    var oddasr_log = function(...msg){
        console.log(ASR_MODULE_NAME , ":", msg);
    }

    function log(isEnableLog  , onLog )
    {
        return function(...msg){
            if(isEnableLog)
            {    
                if(onLog != null)
                    onLog(ASR_MODULE_NAME , msg);
                else
                    console.log(ASR_MODULE_NAME + ":" , msg);
            }
        }
    }

/**
 * @description 初始化OddAsr库
 * @param {object} [option]                     -   解构参数库日志参数
 * @param {bool} [option.isEnableLog=false]     -   是否打开日志
 * @param {function} [option.onLog=null]        -   日志回调函数
 * @param {object} [option={}]                  -   解构参数库初始化参数
 * @returns {CODE}                              -   状态码
 * @global
 * @example 
 * OddAsr.init();
 **/
function init( { isEnableLog = false , onLog = null }={},{}={}){
    oddasr_log = log(isEnableLog , onLog); 
    return CODE.ASR_ERROR_NONE;
}

/**
 * @description 销毁OddAsr库
 * @global
 * @example 
 * OddAsr.release();
 **/
function release({serveraddr = null, client=null}){
    oddasr_log("release");
    // let xhr = new XMLHttpRequest()
    // let data = {'ws_addr':client.addr, 'id': client.id}
    // xhr.open("POST" , serveraddr + "/v1/asr/open/release" , true)
    // xhr.setRequestHeader('Content-type','application/json')
    // xhr.onreadystatechange = function() {
    //     if(xhr.readyState == XMLHttpRequest.DONE) {
    //         if(xhr.status != 200) {
    //             oddasr_log(xhr.responseURL + ' status ' + xhr.status)
    //         }
    //         msg = JSON.parse(xhr.responseText)
    //         if(msg.error_code != 0) {
    //             oddasr_log(xhr.responseText)
    //         }
    //     }
    // }
    // oddasr_log(data)
    // let msg = JSON.stringify(data)
    // oddasr_log(msg)
    // xhr.send(msg)
}

/**
 * @description 创建{@link ODDASRCli}识别对象
 * @returns {ODDASRCli}                    -   {@link ODDASRCli}对象
 * @global
 * @example 
 * let client = OddAsr.createAsrInstance();
 **/
function createAsrInstance(){ oddasr_log("createAsrInstance"); return new ODDASRCli(); }

/**
 * @description 销毁{@link ODDASRCli}识别对象
 * @param {ODDASRCli} client                  -   {@link ODDASRCli}对象
 * @global 
 * @example 
 * OddAsr.destoryAsrInstance(client);
 **/
function destoryAsrInstance(client){ oddasr_log("destoryAsrInstance"); client.destory();return CODE.ASR_ERROR_NONE;}

/**
 * @description 获取OddAsr库版本号
*  @returns {string}                    -   OddAsr的版本号
 * @global
 * @example 
 * OddAsr.getVersion();
 **/
function getVersion()
{
    oddasr_log("getVersion");
    return ASR_MODULE_VERSION;
}

/**
 * @description 设置Asr的选项
 * @param {object} [option]                     -   解构参数库日志参数
 * @param {int} [option.type=0]             -   选项类似 0 敏感词 1 热词
 * @param {object} [option.param={}]            -   选项参数{'serveraddr':'' , 'token':'' , 'unique_id':'','words':['1','2']}
 * @param {function} [option.onResult=function (result , content){}]       -   回调函数
 * @param {any} {content}                       -   回调上下文
 * @global
 * @example 
 * var arg = {'type':0 ,'param':{'serveraddr':'http://10.67.20.59:7966','token':'xxx','hotwords_type':0,'unique_id':'123456','words':['你好','大家']}}
 * arg.onResult = function (result , content){
 *       console.log(result , data)
 *   }
 * OddAsr.setAsrOption(arg)
 **/
function setAsrOption({type = 0 , param = {} , onResult = function (result , content){}} , content = null)
{  
    let xhr = new XMLHttpRequest();
    if(type == 0)
        xhr.open("POST" , param["serveraddr"] + "/v1/asr/sensitivewords" , true);
    else
        xhr.open("POST" , param["serveraddr"] + "/v1/asr/hotwords", true);
    xhr.setRequestHeader('Content-type','application/json');
    xhr.onreadystatechange = function(){
        if(xhr.readyState == XMLHttpRequest.DONE)
        {
            if(xhr.status != 200)
            {
                oddasr_log(xhr.responseURL + ' status ' + xhr.status);
                return onResult(CODE.ASR_ERROR_INTER , null);
            }
            msg = JSON.parse(xhr.responseText);
            if(msg.error_code != 0)
            {
                oddasr_log(xhr.responseText);
                return onResult(CODE.ASR_ERROR_INTER,null);
            }
            return onResult(CODE.ASR_ERROR_NONE);
        }
    }
    xhr.send(JSON.stringify(param));
}

/**
 * @description 获取Asr的选项设置
 * @param {object} [option]                     -   解构参数库日志参数
 * @param {int} [option.type=0]                 -   选项类似 0 敏感词 1 热词
 * @param {object} [option.param={}]            -   选项参数{'serveraddr':'' , 'token':'' , 'unique_id':'','words':['1','2']}
 * @param {function} [option.onResult=function (result , content , data){}]       -   回调函数
 * @param {any} {content}                       -   回调上下文
 * @global
 * @example 
 * var arg = {'type':0 ,'param':{'serveraddr':'http://10.67.20.59:7966','token':'xxx','hotwords_type':0,'unique_id':'123456','words':['你好','大家']}}
 * arg.onResult = function (result , content){
 *       console.log(result , data)
 *   }
 * OddAsr.getAsrOption(arg)
 **/
function getAsrOption({type = 0 , param = {} , onResult = function (result  , content , data ){}} , content=null )
{
    let xhr = new XMLHttpRequest()
    if(type == 0)
        xhr.open("GET" , param["serveraddr"] + "/v1/asr/sensitivewords/unique_id/"+param["unique_id"] + "?token=" + param["token"] , true)
    else
        xhr.open("GET" , param["serveraddr"] + "/v1/asr/hotwords/unique_id/"+param["unique_id"] + "/hotwords_type/" + param["hotwords_type"] + "?token=" + param["token"], true)
    xhr.setRequestHeader('Content-type','application/json')
    xhr.onreadystatechange = function(){
        if(xhr.readyState == XMLHttpRequest.DONE)
        {
            if(xhr.status != 200)
            {   
                oddasr_log(xhr.responseURL + 'status ' + xhr.status)
                return onResult(CODE.ASR_ERROR_INTER , null)
            }
            msg = JSON.parse(xhr.responseText)
            if(msg.error_code != 0)
            {   
                oddasr_log(xhr.responseText)
                return onResult(CODE.ASR_ERROR_INTER,null)             
            }
            return onResult(CODE.ASR_ERROR_NONE,msg.data)       
        }
    }
    xhr.send(null)  
}

/**
 * ODDASRCli识别对象
 * 
 */
class ODDASRCli
{
    constructor()
    {
        this.state = ASR_CLIENT_INIT;
        this.ws = null;
        this.token = null;
    }
    
    /**
     * @description 初始化{@link ODDASRCli}对象,设置回调函数
     * @param {object}   [option]                                                   -   解构参数回调对象类
     * @param {onWarning} [option.onWarning=function(warningType,content){}]        -   消息警告回调
     * @param {onError} [option.onError=function(errorType,content){}]              -   消息错误回调
     * @param {onRelease} [option.onRelease=function(result){}]                     -   释放对象回调
     * @param {onStart} [option.onStart=function(result,sessionid){}]               -   会话开始回调
     * @param {onStop} [option.onStop=function(result){}]                           -   会话结束回调
     * @param {onRecogResult} [option.onRecogResult=function(result){}]             -   识别结果回调
     * @param {onCtrl} [option.onCtrl=function(result,msg_id){}]                    -   参数查询与设置
     * @returns {CODE}                                                              -   状态码
     * @example 
     * client.init({onRecogResult:function(result){console.log(result.text);}});
     **/
    init( {onWarning = function(warningType,content){} ,
        onError = function(errorType,content){} ,
        onRelease = function(result){} ,
        onStart= function(result,sessionid){},       
        onStop = function (result) {},
        onEnstable = function () {},
        onRecogResult=function(result = {bgTime = 0 , edTime = 0 , fin = 0 , text = ''} = {}){}}= {},
        onCtrl = function(result,msg_id){})
    {
        oddasr_log('ODDASRCli.init');
        this.onWarning = onWarning
        this.onError = onError
        this.onRelease = onRelease
        this.onStart = onStart
        this.onEnstable = onEnstable
        this.onRecogResult = onRecogResult
        this.onStop = onStop
        this.onCtrl = onCtrl
        return CODE.ASR_ERROR_NONE;
    }

    onOpen(e){
        oddasr_log('ODDASRCli.onOpen')
        this.state = ASR_CLIENT_CONNECTED;

        let start = {"name": "StartTranscription", "message_id": "", "token": "", "task_id": ""};

        let msg = JSON.stringify(start);
        this.ws.send(msg);
        this.state = ASR_CLIENT_SESSION_STARTING;
        this.onEnstable();
    }
    onClose(e){
        oddasr_log('ODDASRCli.onClose')
        if(this.state != ASR_CLIENT_SESSION_STOPED &&
            this.state != ASR_CLIENT_EXCEPTION &&
            this.state != ASR_CLIENT_DESTORYING &&
            this.state != ASR_CLIENT_DESTORYED)
            {
                this.onError(CODE.ASR_ERROR_INTER , 'disconnect from server! state:' + this.state);
            }
            this.state = ASR_CLIENT_CLOSED;
            this.ws = null;
    }

    onMessage(e){
        oddasr_log("onMessage: " + e.data);
        let j = JSON.parse(e.data)
        if(j == null)
            this.onError(CODE.ASR_ERROR_INTER,'json is not valid!');

        /*
         {
            \"header\": 
            {
                \"message_id\": \"\", \"name\": \"SentenceBegin\", \"namespace\": \"SpeechTranscriber\", \"status\": 0, \"status_text\": \"\", \"task_id\": \"463e1c86-733a-11f0-8cd0-5c879c002fd9\"
            }, 
            \"payload\": 
            {
                \"begin_time\": 0, \"confidence\": 1.0, \"index\": 0, \"result\": \"\", \"time\": 0
            }
        }
         */

        if (j["header"]["name"] == 'SentenceBegin') {
            this.state = ASR_CLIENT_SESSION_ESTABLISHED;
            return this.onStart(CODE.ASR_ERROR_NONE , j['header']['task_id'])
        }
        else if (j["header"]["name"] == 'SentenceEnd') {
            /*
            {
                "header": 
                {
                    "message_id": "", "name": "SentenceEnd", "namespace": "SpeechTranscriber", "status": 0, "status_text": "", "task_id": ""
                }, 
                "payload": 
                {
                    "begin_time": 608.0, "confidence": 1.0, "index": 0, "result": 
                    [
                        {"key": "rand_key_M5jnanQRU85hV", "text": "\u55ef"}
                    ], "time": 0
                }
            }
            */
            const res = j['payload'];
            if (res['result'] != "") {
                this.onRecogResult({bgTime:res['begin_time'],
                    edTime:res['time'],
                    fin:1, // res['fin'],
                    text:"[1]" + res['result']});
            }
        }
        else if (j["header"]["name"] == 'TranscriptionResultChanged') {
            const res = j['payload'];
            if (res['result'] != "") {
                this.onRecogResult({bgTime:res['begin_time'],
                    edTime:res['time'],
                    fin: 1, // res['fin'],
                    text: "[0]" + res['result']});
            }
        }

        // else if(j['msg_type'] == 'START_SESSION_RES')
        // {
        //     let code = j['msg_code'];
        //     if(code == 0)
        //     {  
        //         this.state = ASR_CLIENT_SESSION_ESTABLISHED;
        //         return this.onStart(CODE.ASR_ERROR_NONE , j['msg_data']['session_id'])
        //     }
        //     else if(code == EM_MAI_OPENSDK_CREATE_ENGINE_ERROR) 
        //     {
        //        this.state = ASR_CLIENT_EXCEPTION;
        //        this.ws.close();
        //        return this.onStart(CODE.ASR_ERROR_ENIGNE , j['msg_desc']);
        //     }
        //     else if(code == EM_MAI_JDLSERVER_ASR_ID_NOVALID)
        //     {
        //         this.state = ASR_CLIENT_EXCEPTION;
        //         this.ws.close();
        //         return this.onStart(CODE.ASR_ID_NO_VALID , j["msg_desc"]);
        //     }
        //     else{
        //         this.state = ASR_CLIENT_EXCEPTION;
        //         this.ws.close();
        //         return this.onStart(CODE.ASR_ERROR_INTER , j['msg_desc']);
        //     }
        // }
        // else if(j['msg_type'] == 'RECOGNITION_TEXT')
        // {
        //     const res = j['msg_data'];
        //     this.onRecogResult({bgTime:res['bgTime'],
        //         edTime:res['edTime'],
        //         fin:res['fin'],
        //         text:res['text']});
        // }
        // else if(j['msg_type'] == 'STOP_SESSION_RES')
        // {
        //    this.state = ASR_CLIENT_SESSION_STOPED;
        //    this.ws.close();
        //    return this.onStop(CODE.ASR_ERROR_NONE); 
        // }
        // else if(j['msg_type'] == 'EXCEPTION_NTF')
        // {
        //     this.state = ASR_CLIENT_EXCEPTION;
        //     this.ws.close();
        //     return this.onError(CODE.ASR_ERROR_INTER , j['msg_desc']);
        // }
        // else if(j['msg_type'] == 'SESSION_CTRL_RES')
        // {
        //     let code = j['msg_code'];
        //     if(code == 0)
        //         this.onCtrl(CODE.ASR_ERROR_NONE , j['msg_id'])
        //     else
        //         this.onCtrl(CODE.ASR_ERROR_INTER , j['msg_id'])
        // }
    }
    onError1(e){
        oddasr_log('ODDASRCli.onError');
        this.state = ASR_CLIENT_CLOSED;
        this.onStart(CODE.ASR_ERROR_NET , null);
        this.ws = null;
    }

     /**
     * @description 开始会话
     * @param {object} [option]                                            -   解构参数授权对象参数
     * @param {string} [option.token]                                      -   授权token
     * @param {string} [option.serveraddr='ws://oddmeta.com:8101/']        -   服务器地址
     * @param {string} [option.format='pcm']                               -   音频格式
     * @param {string} {option.samplerate=16000}                           -   音频采样率
     * @returns {CODE}   -   状态码
     * @example 
     * client.start({token:'xxx',serveraddr:'xxx'});                                                       
     **/
    start( {token,serveraddr,format='pcm' , samplerate = 16000 ,autosave = false, meeting_info = {'name':'unknow_name','address':'unknow_address','participant':'none','remark':''}} = {})
    {
        oddasr_log('ODDASRCli.start, token:' + token + ', serveraddr:' + serveraddr + ', format:' + format + ', samplerate:' + samplerate + ', autosave:' + autosave + ', meeting_info:' + meeting_info);

        this.state = ASR_CLIENT_CONNECTING;
        this.meeting_info = meeting_info
        this.autosave = autosave
        this.format = format
        this.samplerate = samplerate

        if (serveraddr == "")
            this.addr = "ws://127.0.0.1:8101";
        else
            this.addr = serveraddr;

        oddasr_log('get addr ' + this.addr  + " id " + this.id);
        try{
            let ws = new WebSocket(this.addr);
            this.ws = ws;

            ws.onopen = e => this.onOpen(e);
            ws.onmessage = e => this.onMessage(e);
            ws.onclose = e => this.onClose(e);
            ws.onerror= e => this.onError1(e);
        }
        catch(error){
            oddasr_log('ODDASRCli.start ' + error);
            return CODE.ASR_ERROR_NET;
        }
        
        return CODE.ASR_ERROR_NONE;
    }

    /**
     * @description 结束会话
     * @returns {CODE}                                                          -   状态码
     * @example 
     * client.stop(); 
     **/
    stop()
    {
        oddasr_log('ODDASRCli.stop');
        if (this.ws && this.state == ASR_CLIENT_SESSION_ESTABLISHED) {
            let stop = {'service_type':'ASR','msg_type':'STOP_SESSION_REQ'};
            let msg = JSON.stringify(stop);
            this.ws.send(msg);
        }
        this.state = ASR_CLIENT_SESSION_STOPING;
        return CODE.ASR_ERROR_NONE;
    }

    /**
     * @description 传输音频PCM数据,目前支持16k采样,16bit,单通道(mono)的数据
     * @param {object}  option                                          -   解构参数音频帧对象
     * @param {int}  [option.channelCount=1]                            -   通道数目
     * @param {int}  [option.sampleRate=16000]                          -   采样率
     * @param {int}  [option.bitWidth=16]                               -   采样位数
     * @param {ArrayBuffer}  option.data                                -   音频数据
     * @returns {CODE}                                                  -   状态码
     * @example 
     * client.feed({data:data}); 
     **/
    feed({channelCount=1,sampleRate=16000,bitWidth=16,data}={} )
    {
        if(channelCount != 1 ||
            (sampleRate != 16000 && sampleRate != 32000 && sampleRate != 48000) ||
            bitWidth != 16)
        {
            oddasr_log('ODDASRCli.feed arg error');
            return CODE.ASR_ERROR_ARGS;
        }

        if(this.state != ASR_CLIENT_SESSION_ESTABLISHED)
        {
            oddasr_log('ODDASRCli.feed state error');
            // 暂时返回成功，避免采集快于跟后端处理数据
            // return CODE.ASR_ERROR_STATE;
            return CODE.ASR_ERROR_NONE;
        }
        this.ws.send(data);
        return CODE.ASR_ERROR_NONE;
    }

    /**
     * @description 敏感词/热词启停
     * @param {object}  option                                          -   解构参数音频帧对象
     * @param {string}  [option.unqiue_id='']                           -   唯一标识
     * @param {int}  [option.type=0]                                    -   敏感词/热词
     * @param {bool}  [option.enable=true]                              -   启用/停止
     * @example 
     * client.ctrl({unqiue_id='2222-3333-4444-5555',type=0,enable=true});
     **/
    ctrl({unqiue_id='',type=0,enable=true,msg_id=''})
    {
        oddasr_log('ODDASRCli.ctrl')   
        // let ctrl_msg = {'unique_id':unqiue_id , 'enable':enable}
        // let top_msg = {'msg_id':msg_id,'msg_type':'SESSION_CTRL_REQ','service_type':'ASR' , 'msg_data':ctrl_msg, 'type':type }
        // console.log(top_msg)
        // let msg = JSON.stringify(top_msg);
        // this.ws.send(msg);
        return CODE.ASR_ERROR_NONE;
    }


    destory()
    {
        oddasr_log('ODDASRCli.destory');
        this.state = ASR_CLIENT_DESTORYING;
        if(this.ws != null)
            this.ws.close();
        this.state = ASR_CLIENT_DESTORYED;
        this.onRelease(CODE.ASR_ERROR_NONE);
    }

}

return {init:init,
    createAsrInstance:createAsrInstance,
    release:release,
    getVersion:getVersion,
    destoryAsrInstance:destoryAsrInstance,
    CODE:CODE,
    setAsrOption:setAsrOption,
    getAsrOption,getAsrOption
}
}();
