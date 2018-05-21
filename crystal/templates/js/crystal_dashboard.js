
var vue = new Vue({
    el: '#vue-app',
    data: {
        current_project: "",
        current_run: "",
        current_variables: "",
        current_graph_raw_values: [],
        all_projects: {},
        all_current_runs: {},
        entered_refresh_time: '',
        refresh_time: 5000,
        start_refreshing: false,
        refresh_button_text: 'Start Refreshing',
        timer: '',
        run_plots_init: false,
    },
    methods: {
        refresh: function () {
            var rq = new XMLHttpRequest();

            console.log("refresh");

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
                        vm.all_current_runs = " ";
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
                        vm.current_variables = " ";
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

            if (this.current_variables === '') {
                console.log("Current variables are non.");
                this.run_plots_init = true;  // Haven't received any variables from the server
                return false;
            }

            for (var variable in this.current_variables) {
                current_value = this.current_variables[variable];
                var layout = {
                    showlegend: true,
                    autosize: true,
                    margin: {
                        b: 30,
                        t: 20,
                        l: 50,
                        r: 50,
                    },
                };
                var trace = [{
                    name: current_value,
                    x: [],
                    y: [],
                    type: 'scatter',
                }];
                Plotly.newPlot(current_value, trace, layout, {displayModeBar: false});
                console.log("Running plots!");
            }
            this.set_refresh();
            return true;
        },
        set_run: function (run_selected) {
            this.current_run = run_selected;
            this.get_variables();
            this.run_plots_init = true;
        },
        set_refresh: function () {

            if (this.run_plots_init === true){
                console.log("Initial Run");
                clearInterval(this.timer);
                this.refresh_button_text = "Stop Refreshing";
                refresh();
                this.timer = setInterval(function () {
                    refresh();
                }, this.refresh_time);
                return;
            }

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
            this.start_refreshing = !this.start_refreshing;
            console.log("Refresh toggled");
        },
        set_refresh_interval: function () {
            this.refresh_time = parseInt(this.entered_refresh_time) * 1000;  // time needed in ms
            clearInterval(this.timer);
            this.timer = setInterval(function () {
                refresh();
            }, this.refresh_time);
            console.log("Refresh_interval set to " + this.refresh_time);
        },
        download_graph: function (id) {
            Plotly.downloadImage(id, {format: 'png', filename: id});
        },
        get_graph_csv: function (id) {
            var rq = new XMLHttpRequest();

            rq.onreadystatechange = function(vm) {
                if (this.readyState === XMLHttpRequest.DONE) {
                    if (this.status === 200) {
                        // vm.current_graph_raw_values = JSON.parse(this.responseText);
                        var blob = new Blob([this.responseText]);
                        if (window.navigator.msSaveOrOpenBlob)  // IE hack; see http://msdn.microsoft.com/en-us/library/ie/hh779016.aspx
                            window.navigator.msSaveBlob(blob, vm.current_run+"_"+id+".csv");
                        else
                        {
                            var a = window.document.createElement("a");
                            a.href = window.URL.createObjectURL(blob, {type: "text/plain"});
                            a.download = vm.current_run+"_"+id+".csv";
                            document.body.appendChild(a);
                            a.click();  // IE: "Access is denied"; see: https://connect.microsoft.com/IE/feedback/details/797361/ie-10-treats-blob-url-as-cross-origin-and-denies-access
                            document.body.removeChild(a);
                        }
                    } else {
                        vm.current_graph_raw_values = " ";
                    }
                }
            }.bind(rq, this);

            rq.open("POST", "/get_graph_csv", true);
            rq.setRequestHeader('content-type', 'application/x-www-form-urlencoded;charset=UTF-8');
            rq.send("selected_variable_table="+this.current_run+"_"+id);
        }
    },
    
    // Lifecycle hook
    updated() {
        if (this.run_plots_init === true) {
            console.log("Run plots init is set to true");
            plots_shown = this.show_plots();
            if (plots_shown) {
                this.run_plots_init = false;
            }
        }
    }

});


function refresh() {
    vue.refresh();
}