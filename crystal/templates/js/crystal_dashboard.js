
let vue_dashboard = new Vue({
    el: '#vue-dashboard',
    data: {
        current_project: "",                     // Selected project
        current_run: "",                         // Selected run
        current_variables: {},                   // Object that will contain the variables to be shown
        current_window: "plots",                 // Which window is the user currently in -> plots, images,
        all_projects: {},                        // Must be an empty Object to show nothing on the DOM
        all_runs: {},                            // Must be an empty Object to show nothing on the DOM
        refresh_time: 5000,                      // Default refresh interval in ms
        refreshing: false,                       // Set to false as initially refreshing is done when the plots are shown
        refresh_button_text: 'Start Refreshing', // Refresh button text
        timer: '',                               // timer instance that will be used later
        run_plots_init: false,                   // Ensures that plots are shown only when the DOM has been updated
                                                 // with the required ids that are used by plotly
        showModal: false,
    },
    methods: {
        refresh: function () {
            /*
            Use an Async request to check and retrieve variable values that are updated.
             */
            console.log("refreshing");
            let rq = new XMLHttpRequest();
            rq.onreadystatechange = function(vm) {
                if (this.readyState === XMLHttpRequest.DONE) {
                    if (this.status === 200) {
                        var receivedJSON = JSON.parse(rq.responseText);
                        for (var k in vm.current_variables) {
                            let current_value = vm.current_variables[k];
                            var update = {
                                x:  [receivedJSON[current_value]['x']],
                                y: [receivedJSON[current_value]['y']]
                            };
                            // console.log(receivedJSON[current_value]['x']);
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
            /*
            Use an Async request to get JSON file containing the projects available in the database.
            Upon receiving a response, sets the all_projects variable with the received JSON object.
            As soon this variable changes Vue updates the DOM to show them on the dropdown menu.
             */
            let rq = new XMLHttpRequest();
            rq.onreadystatechange = function(vm) {
                if (this.readyState === XMLHttpRequest.DONE) {
                    if (this.status === 200) {
                        vm.all_projects = JSON.parse(this.responseText);
                    } else {
                        vm.all_projects = {};
                    }
                }
            }.bind(rq, this);
            rq.open("GET", "/get_projects");
            rq.send();
        },
        get_runs: function() {
            /*
            Use an Async request to get JSON file containing runs available for a selected project.
            Upon receiving a response, sets the all_runs variable with the received JSON object.
            As soon this variable changes Vue updates the DOM to show them on the dropdown menu.
             */
            let rq = new XMLHttpRequest();
            rq.onreadystatechange = function(vm) {
                if (this.readyState === XMLHttpRequest.DONE) {
                    if (this.status === 200) {
                        vm.all_runs = JSON.parse(this.responseText);
                    } else {
                        vm.all_runs = {};
                    }
                }
            }.bind(rq, this);
            rq.open("POST", "/get_runs", true);
            rq.setRequestHeader('content-type', 'application/x-www-form-urlencoded;charset=UTF-8');
            rq.send("selected_project="+this.current_project);
        },
        get_variables: function () {
            /*
            Use an Async request to get JSON file containing all variables available for a selected project.
            Upon receiving a response, sets the current_variables variable with the received JSON object.
            As soon this variable changes Vue updates the div id of the cards image that shows the plotly plots.
             */
            let rq = new XMLHttpRequest();
            rq.onreadystatechange = function(vm) {
                if (this.readyState === XMLHttpRequest.DONE) {
                    if (this.status === 200) {
                        vm.current_variables = JSON.parse(this.responseText);
                        this.run_plots_init = true;
                    } else {
                        vm.current_variables = {};
                    }
                }
            }.bind(rq, this);
            rq.open("POST", "/get_variables", true);
            rq.setRequestHeader('content-type', 'application/x-www-form-urlencoded;charset=UTF-8');
            rq.send("selected_run="+this.current_run);
        },
        set_project: function (project_selected) {
            /*
            Updates the current_project variable with the project selected using the dropdown menu.
             */
            this.current_project = project_selected;
        },
        show_plots: function () {
            /*
            Show all the plots on the DOM. This function must be called only after all the required div ids are
            updated on the DOM.
            return: true  -> Plots shown
                    false -> Plots not shown as there are no variables available
             */
            if (Object.keys(this.current_variables).length === 0) {
                console.log("Current variables are non.");
                this.run_plots_init = true;  // Haven't received any variables from the server
                return false;
            }
            for (let k in this.current_variables) {
                current_value = this.current_variables[k];
                var layout = {
                    showlegend: true,
                    autosize: true,
                    margin: {b: 30, t: 20, l: 50, r: 50},
                };
                var trace = [{
                    name: current_value,
                    x: [],
                    y: [],
                    type: 'scatter',
                }];
                Plotly.newPlot(current_value, trace, layout, {displayModeBar: false});
                console.log("Showing plots!");
            }
            this.toggle_refresh();
            return true;
        },
        set_run: function (run_selected) {
            /*
            Updates the current_run variable with the run selected using the dropdown menu.
            Gets the variables that need to plotted and also ensures that the plots are shown.
             */
            this.current_run = run_selected;
            this.get_variables();
            this.run_plots_init = true;
        },
        toggle_refresh: function () {
            /*
            Toggles the refresh button.
            When called with run_plots_init set to true, clears all previous timers and starts a new one.
            If not then, just toggles the refresh button.
             */

            // Check if this is the init run
            if (this.run_plots_init === true) {
                console.log("Initial Run");
                clearInterval(this.timer);
                this.refresh_button_text = "Stop Refreshing";
                refresh();
                this.timer = setInterval(function () {
                    refresh();
                }, this.refresh_time);
                return;
            }

            if (!this.refreshing) {
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
            this.refreshing = !this.refreshing;
            console.log("Refresh toggled");
        },
        download_graph: function (id) {
            /*
            Call the appropriate plotly function to download the graph.
             */
            Plotly.downloadImage(id, {format: 'png', filename: id});
        },
        get_graph_csv: function (id) {
            /*
            Download a CSV file containing the data of the selected plot.
             */
            let rq = new XMLHttpRequest();

            rq.onreadystatechange = function(vm) {
                if (this.readyState === XMLHttpRequest.DONE) {
                    if (this.status === 200) {
                        let blob = new Blob([this.responseText]);
                        // IE hack;
                        if (window.navigator.msSaveOrOpenBlob) {
                            window.navigator.msSaveBlob(blob, vm.current_run+"_"+id+".csv");
                        }
                        else {
                            let a = window.document.createElement("a");
                            a.href = window.URL.createObjectURL(blob, {type: "text/plain"});
                            a.download = vm.current_run+"_"+id+".csv";
                            document.body.appendChild(a);
                            a.click();
                            document.body.removeChild(a);
                        }
                    } else {
                        console.log("Not able to download the requested CV file.")
                    }
                }
            }.bind(rq, this);
            rq.open("POST", "/get_graph_csv", true);
            rq.setRequestHeader('content-type', 'application/x-www-form-urlencoded;charset=UTF-8');
            rq.send("selected_variable_table="+this.current_run+"_"+id);
        },
        show_images_window: function () {
            console.log("show_images_window");
            // Stop refreshing, not using toggle as it messes with the timer and does not stop it.
            clearInterval(this.timer);
            this.refresh_button_text = "Start Refreshing";
            console.log("Refreshing for plots stopped.");
            // Change DOM
            this.current_window = "images";
        },
        show_plots_window: function () {
            console.log("show_plots_window");
            this.current_window = "plots";
            // Completely refresh by asking the variable values again from the server
            this.get_variables();
            this.run_plots_init = true;
        },
        show_mouse_over: function (text) {
            document.getElementById(text+"_text").innerHTML = text;
        },
        hide_mouse_over: function (text) {
            document.getElementById(text+"_text").innerHTML = "";
        }
    },
    
    // Lifecycle hook to show plots only after the DOM has been updated with the required ids
    updated() {
        /*
        Show plots only when the DOM is updated with the required ids.
         */
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
    vue_dashboard.refresh();
}

// register modal component
Vue.component('modal', {
    template: '#modal-template',
    data: function() {
        return {
            entered_refresh_time: "",                // Used for two way data binding
            title: "Project management",
        }
    },
    methods: {
        set_refresh_interval: function () {
            /*
            Change the refresh interval to the desired value.
            This function uses two way data binding to transfer the entered value.
             */
            vue_dashboard.refresh_time = parseInt(this.entered_refresh_time) * 1000;  // time needed in ms
            clearInterval(vue_dashboard.timer);
            vue_dashboard.timer = setInterval(function () {
                refresh();
            }, vue_dashboard.refresh_time);
            console.log("Refresh_interval set to " + vue_dashboard.refresh_time);
        },
        close_project_management: function (event) {
            if (event.target.className === "modal-wrapper") {
                this.$emit('close');
            }
        }
    }
});

