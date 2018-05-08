
new Vue({
    el: '#vue-app',
    data: {
        current_project: "",
        current_run: "",
        current_variables: {},
        all_projects: {},
        all_current_runs: {},
    },
    methods: {
        refresh: function () {
            console.log("Refresh Clicked");
            var xmlhhtp = new XMLHttpRequest(),
                method = "GET",
                url = "%%url_for('update')%%";

            xmlhhtp.open(method, url, true);
            xmlhhtp.onreadystatechange = function () {
                if (this.readyState === XMLHttpRequest.DONE && this.status === 200){
                    console.log(JSON.parse(xmlhhtp.responseText));

                    var receivedJSON = JSON.parse(xmlhhtp.responseText);

                    for (var variable in this.current_variables) {
                        let current_value = this.current_variables[variable];
                        var update = {
                            x:  [receivedJSON[current_value]['x']],
                            y: [receivedJSON[current_value]['y']]
                        };

                        console.log(receivedJSON[current_value]['x']);

                        Plotly.extendTraces(current_value, update, [0]);
                    }
                }
            };
            xmlhhtp.send()
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

            rq.open("GET", "%%url_for('get_projects')%%");
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

            rq.open("POST", "%%url_for('get_runs')%%", true);
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
                        for (var variable in vm.current_variables) {
                            current_value = vm.current_variables[variable];
                            var trace = [{
                                x: [],
                                y: [],
                                type: 'scatter'
                            }];
                            Plotly.newPlot(current_value, trace);
                        }
                    } else {
                        vm.current_variables = "Request Failed";
                    }
                }
            }.bind(rq, this);

            rq.open("POST", "%%url_for('get_variables')%%", true);
            rq.setRequestHeader('content-type', 'application/x-www-form-urlencoded;charset=UTF-8');
            rq.send("selected_run="+this.current_run);
        },
        set_project: function (project_selected) {
            this.current_project = project_selected;
        },
        set_run: function (run_selected) {
            this.current_run = run_selected;
            this.get_variables();
        },

    }
});

