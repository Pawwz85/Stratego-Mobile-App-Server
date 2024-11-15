
export class Clock{
    constructor(tick_rate){
        this.clock_target = {mode: "count_down", value: 130000};
        this.observers = [];
        this.time_left_ms = 130000; // time left to 
        this.tick_rate_ms = tick_rate;
        this.__timer = setInterval(this.__clock_tick, this.tick_rate_ms, this);

        this.notify_observers();
    }

    notify_observers(){
        for (let o of this.observers) {
            o.refresh_clock(this.time_left_ms)
        }
    }

    update_clock_target(clock){
        this.clock_target = clock
        this.clock_target.value = this.clock_target.value?? 0;
        this.time_left_ms = (this.clock_target.mode == "paused") ? clock?.value : clock?.value - Date.now();
        if(this.time_left_ms < 0)
            this.time_left_ms = 0
        
        this.notify_observers(); // Force refresh of all clocks
    }

    __clock_tick(clock_instance) {
        let This = clock_instance;
        if (This.clock_target.mode == "count_down" && This.time_left_ms > 0) {
            This.time_left_ms = This.clock_target.value - Date.now();
            if(This.time_left_ms < 0)
                This.time_left_ms = 0;
            This.notify_observers();
        }
    }

    remove_observer(observer){
        this.observers = this.observers.filter(o => o !== observer);
    }
}

export class SimpleClock{
    constructor(){
        this.time_left_ms = 0;
        this.__rect = null;
        this.__text = null;
        this.element = this.__init_element();
    }

    __init_element(){
        let result = document.createElementNS("http://www.w3.org/2000/svg", "svg");
        result.setAttributeNS(null, "viewBox", "0 0 100 50");

       this.__rect = document.createElementNS("http://www.w3.org/2000/svg", "rect");
       this.__text = document.createElementNS("http://www.w3.org/2000/svg", "text");
       
       this.__rect.setAttributeNS(null, "x", "0");
       this.__rect.setAttributeNS(null, "width", "100")
       this.__rect.setAttributeNS(null, "height", "50");
       this.__rect.setAttributeNS(null, "fill", "black");

       this.__text.setAttributeNS(null, "x", "50%");
       this.__text.setAttributeNS(null, "y", "50%");
       this.__text.setAttribute("fill", "white");
       this.__text.setAttributeNS(null, "dy", ".4em");
       this.__text.setAttributeNS(null, "text-anchor", "middle");
       this.__text.setAttribute("unselectable", "on");
       this.__text.style.pointerEvents = "none";
       this.__text.style.userSelect = "none";
       this.__text.textContent = this.format_time(this.time_left_ms)
       result.append(this.__rect, this.__text);
       return result;
    }

    refresh_clock(value){
        this.time_left_ms = value;
        this.__text.textContent = this.format_time(value);
    }

    format_time(time_ms){

        if (time_ms < 10000){
            // Player has les than 10s, display remaing time in form ss.m
            let seconds = Math.floor(time_ms/1000);
            let remainder = time_ms - 1000*seconds;
            let hundreths_of_seconds =  Math.floor(remainder/100);
            return "" + seconds + "." + hundreths_of_seconds;
        } else {
            let minutes = Math.floor(time_ms/60000);
            let seconds = Math.floor((time_ms - 60000*minutes)/1000)

            if (seconds < 10)
                seconds = "0" + seconds;

            return "" + minutes + ":" + seconds;
        }
    }
}