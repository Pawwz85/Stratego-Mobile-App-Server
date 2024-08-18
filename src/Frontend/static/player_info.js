export class TimerModel{
    constructor(){
        this.stop = true;
        this.timer_ms = 10000; // the amount of timer displays in miliseconds
        this.step_ms = 100; //step time in mili seconds
        this.observers = [];
    }
    __step(){
        if(!this.stop){
            this.timer_ms -= this.step_ms; 
            if(this.timer_ms <= 0){
                this.timer_ms = 0;
                this.stop = false;
            }
            setTimeout(this.__step, this.step_ms);
        }
    }

    start(time_ms){
        this.stop = false;
        this.timer_ms = time_ms;
        setTimeout(this.__step, this.step_ms)
    }

    notify_observers(){
        for (let observer of this.observers){
            observer.update(this);
        }
    }
}

export class TimerView{
    constructor(model){
        this.timerModel = model;
        this.timerElement = this.__create_element();
        this.refresh();
    }

    __number_to_string(time_ms){
        let result = "";
        const ms = time_ms%1000;
        const ss = Math.floor(time_ms/1000)%60;
        const mm = Math.floor(time_ms/60000)%60;

        const to_electronic_display = nr => {
            return (0 <= nr && nr < 10)? +"0" + nr: + nr;
        }

        return to_electronic_display(mm) + ":" + to_electronic_display(ss);
    }

    __create_element(){
        let result = document.createElement("h1");
        return result;
    }

    update(model){
        this.timerElement.textContent = this.__number_to_string(model.timer_ms);
    }

    refresh(){
        this.update(this.timerModel);
    }
}

export class PlayerInfoModel{
    constructor(){
        this.username = "";
        this.profile_picture = "";
        this.observers = [];
    }

    setUsername(username){
        this.username = username;
        this.notify_observers();
    }

    notify_observers(){
        for(let obs of this.observers)
            obs.update(this);
    }
}

export class PlayerInfoView{
    constructor(model){
        this.model = model;
        this.__username = null;
        this.element = this.__create_element();
        model.observers.push(this);
    }

    refresh(){
        this.update(this.model);
    }

    __create_element(){
        let result = document.createElement("div");
        this.__username = document.createElement("h2");
        return result;
    }

    update(model){
        this.__username.textContent = model.username;
    }
}

export class PlayerInfoFragment{

    constructor(){
        this.model = new PlayerInfoModel();
        this.playerInfoView = new PlayerInfoView(this.model);
        this.timerModel = new TimerModel();
        this.timerView = new TimerView(this.timerModel);
        this.element = document.createElement("div");
        this.onCreate();
    }

    onCreate(){
        this.element.append(this.playerInfoView.element);
        this.element.append(this.timerView.timerElement);
    }
    
    onFocus(){};

    onHide(){};

    onDestroy(){};

} 
