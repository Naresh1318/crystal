
var vue = new Vue({
    el: '#vue-app',
    data: {
        current_project: "",
        current_run: "",
        current_variables: '',
        all_projects: {},
        all_current_runs: {},
        refresh_time: 5000,
        start_refreshing: false,
        refresh_button_text: 'Start Refreshing',
        timer: '',
        run_plots_init: false,
    },
    methods: {
        refresh: function () {
            var rq = new XMLHttpRequest();

            rq.onreadystatechange = function(vm) {
                if (this.readyState === XMLHttpRequest.DONE) {
                    if (this.status === 200) {
                        var receivedJSON = JSON.parse(rq.responseText);
                        for (var variable in vm.current_variables) {
                            let current_value = vm.current_variables[variable];
                            var update = {
                                x:  [receivedJSON[current_value]['x']],
                                y: [receivedJSON[current_value]['y']]
                            };

                            console.log(receivedJSON[current_value]['x']);

                            Plotly.extendTraces(current_value, update, [0]);
                        }
                    } else {
                        console.log("Nothing received");
                    }
                }
            }.bind(rq, this);

            rq.open("POST", "/update", true);
            rq.setRequestHeader('content-type', 'application/x-www-form-urlencoded;charset=UTF-8');
            rq.send("selected_run="+this.current_run);
        },
        get_projects: function() {
            this.all_projects = "";
            var rq = new XMLHttpRequest();

            rq.onreadystatechange = function(vm) {
                if (this.readyState === XMLHttpRequest.DONE) {
                    if (this.status === 200) {
                        vm.all_projects = JSON.parse(this.responseText);
                    } else {
                        vm.all_projects = "Request Failed";
                    }
                }
            }.bind(rq, this);

            rq.open("GET", "/get_projects");
            rq.send();
        },
        get_runs: function() {
            this.all_current_runs = "";

            var rq = new XMLHttpRequest();

            rq.onreadystatechange = function(vm) {
                if (this.readyState === XMLHttpRequest.DONE) {
                    if (this.status === 200) {
                        vm.all_current_runs = JSON.parse(this.responseText);
                    } else {
                        vm.all_current_runs = "Request Failed";
                    }
                }
            }.bind(rq, this);

            rq.open("POST", "/get_runs", true);
            rq.setRequestHeader('content-type', 'application/x-www-form-urlencoded;charset=UTF-8');
            rq.send("selected_project="+this.current_project);
        },
        get_variables: function () {
            this.current_variables = "";

            var rq = new XMLHttpRequest();

            rq.onreadystatechange = function(vm) {
                if (this.readyState === XMLHttpRequest.DONE) {
                    if (this.status === 200) {
                        vm.current_variables = JSON.parse(this.responseText);
                        console.log("Got it!");
                        this.run_plots_init = true;
                    } else {
                        vm.current_variables = "Request Failed";
                    }
                }
            }.bind(rq, this);

            rq.open("POST", "/get_variables", true);
            rq.setRequestHeader('content-type', 'application/x-www-form-urlencoded;charset=UTF-8');
            rq.send("selected_run="+this.current_run);
        },
        set_project: function (project_selected) {
            this.current_project = project_selected;
        },
        show_plots: function () {
            for (var variable in this.current_variables) {
                current_value = this.current_variables[variable];
                var layout = {
                    title: '',
                    showlegend: false
                };
                var trace = [{
                    x: [],
                    y: [],
                    type: 'scatter'
                }];
                Plotly.newPlot(current_value, trace, layout, {displayModeBar: false});
                console.log("Running plots!");
            }
            this.set_refresh();
        },
        set_run: function (run_selected) {
            this.current_run = run_selected;
            this.get_variables();
            this.run_plots_init = true;
            // setTimeout(() => {
            //     this.show_plots();
            // }, 0);
        },
        set_refresh: function () {
            this.start_refreshing = !this.start_refreshing;
            if (!this.start_refreshing) {
                this.refresh_button_text = "Start Refreshing";
                clearInterval(this.timer);
            }
            else {
                this.refresh_button_text = "Stop Refreshing";
                // Refresh once and then start timer, this makes it fell right
                refresh();
                 this.timer = setInterval(function () {
                    refresh();
                }, this.refresh_time);
            }
        },
    },

    // Lifecycle hooks
    updated() {
        if (this.run_plots_init === true) {
            this.show_plots();
            this.run_plots_init = false;
        }
    }


});


function refresh() {
    vue.refresh();
}