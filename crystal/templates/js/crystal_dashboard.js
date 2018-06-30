
// register modal component
modal = Vue.extend({
    template: '#modal-template',
    data: function() {
        return {
            entered_refresh_time: "",                // Used for two way data binding
            entered_smoothing_value: 1.0,
            title: "Project management",
            all_projects: {},
            all_runs: {},
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
        set_smoothing_value: function () {
            /*
            Change the graph smoothing value to the desired value.
            This function uses two way data binding to transfer the entered value.
             */
            vue_dashboard.smoothing_value = parseFloat(this.entered_smoothing_value);
            force();
            console.log("smoothing_value set to " + vue_dashboard.smoothing_value);
        },
        show_project_management: function () {

            // Request all the projects
            let rq = new XMLHttpRequest();
            rq.onreadystatechange = function(vm) {
                if (this.readyState === XMLHttpRequest.DONE) {
                    if (this.status === 200) {
                        vm.all_projects = JSON.parse(this.responseText);
                        for (key in vm.all_projects) {
                            vm.all_runs[vm.all_projects[key]] = {};
                        }
                    } else {
                        vm.all_projects = {};
                    }
                }
            }.bind(rq, this);
            rq.open("GET", "/get_projects");
            rq.send();
        },
        close_project_management: function (event) {
            if (event.target.className === "modal-wrapper") {
                this.showModal = false;
                this.$emit('close');
            }
        },
        get_runs: function(project) {
            /*
            Use an Async request to get JSON file containing runs available for a selected project.
            Upon receiving a response, sets the all_runs variable with the received JSON object.
            As soon this variable changes Vue updates the DOM to show them on the dropdown menu.
             */
            // Check if runs are already requested and close
            if (Object.keys(this.all_runs[project]).length !== 0) {
                this.all_runs[project] = {};
                this.$forceUpdate();
                return;
            }

            // Request all runs
            let rq = new XMLHttpRequest();
            rq.onreadystatechange = function(vm) {
                if (this.readyState === XMLHttpRequest.DONE) {
                    if (this.status === 200) {
                        vm.all_runs[project] = JSON.parse(this.responseText);
                        console.log(vm.all_runs);
                        vm.$forceUpdate();
                    } else {
                        vm.all_runs[project] = {};
                    }
                }
            }.bind(rq, this);
            rq.open("POST", "/get_runs", true);
            rq.setRequestHeader('content-type', 'application/x-www-form-urlencoded;charset=UTF-8');
            rq.send("selected_project="+project);
        },
        delete_run: function (project, run) {
            let r = confirm("Are you sure?");
            if (r === true) {
                // Request all runs
                let selections = {"project": project, "run": run};
                let rq = new XMLHttpRequest();
                rq.onreadystatechange = function(vm) {
                    if (this.readyState === XMLHttpRequest.DONE) {
                        if (this.status === 200) {
                            delete vm.all_runs[project][run];
                            console.log("Deleted run: " + run);
                            vm.$forceUpdate();
                        }
                    }
                }.bind(rq, this);
                rq.open("POST", "/delete_run", true);
                rq.setRequestHeader('content-type', 'application/x-www-form-urlencoded;charset=UTF-8');
                rq.send("selections="+JSON.stringify(selections));
            } else {
                console.log("Nothing deleted! Chill!");
            }
        },
        delete_project: function (project) {
            let r = confirm("Are you sure?");
            if (r === true) {
                // Request all runs
                let selections = {"project": project};
                let rq = new XMLHttpRequest();
                rq.onreadystatechange = function(vm) {
                    if (this.readyState === XMLHttpRequest.DONE) {
                        if (this.status === 200) {
                            delete vm.all_runs[project];
                            console.log("Deleted project: " + project);
                            vm.$forceUpdate();
                        }
                    }
                }.bind(rq, this);
                rq.open("POST", "/delete_project", true);
                rq.setRequestHeader('content-type', 'application/x-www-form-urlencoded;charset=UTF-8');
                rq.send("selections="+JSON.stringify(selections));
            } else {
                console.log("Nothing deleted! Chill!");
            }
        }

    },
    mounted() {
        this.show_project_management();
    },
});

let vue_dashboard = new Vue({
    el: '#vue-dashboard',
    data: {
        current_project: "Select a project",                     // Selected project
        current_run: "Select a run",                         // Selected run
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
        scalar_variable_values: {},              // Might be used later to animate graphs
        heatmap_variable_values: {},
    },
    components: {
        "modal": modal,
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
                        const receivedJSON = JSON.parse(rq.responseText);
                        for (let k in vm.current_variables) {
                            let current_value = vm.current_variables[k];
                            vm.update_plots(current_value, receivedJSON);
                            // console.log(receivedJSON[current_value]['x']);
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
        update_plots: function(current_value, receivedJSON) {
            const plot_type = current_value.split("_")[0];
            if (plot_type === "scalar") {
                let update = {
                    x:  [receivedJSON[current_value]['x']],
                    y: [receivedJSON[current_value]['y']],
                };
                Plotly.extendTraces(current_value, update, [0]);

                //     this.scalar_variable_values[current_value]["x"] = this.scalar_variable_values[current_value]["x"].concat(receivedJSON[current_value]["x"]);
                //     this.scalar_variable_values[current_value]["y"] = this.scalar_variable_values[current_value]["y"].concat(receivedJSON[current_value]["y"]);
                //     Plotly.animate(current_value, {
                //             data: [{
                //                 x: this.scalar_variable_values[current_value]["x"],
                //                 y: this.scalar_variable_values[current_value]["y"]
                //             }],
                //             traces: [0],
                //             layout: layout,
                //         },
                //         {
                //             transition: {
                //                 duration: 500,
                //                 easing: 'cubic-in-out'
                //             }
                //         });
                //
            }
            else if (plot_type === "heatmap") {
                this.heatmap_variable_values[current_value]["vn"] = this.heatmap_variable_values[current_value]["vn"].concat(receivedJSON[current_value]['vn']);
                this.heatmap_variable_values[current_value]["z"] = this.heatmap_variable_values[current_value]["z"].concat(receivedJSON[current_value]['z']);

                let update = {
                    x: [receivedJSON[current_value]['vn'][receivedJSON[current_value]['vn'].length-1]],
                    y: [receivedJSON[current_value]['vn'][receivedJSON[current_value]['vn'].length-1]],
                    z: [receivedJSON[current_value]['z'][receivedJSON[current_value]['z'].length-1]],
                };

                if (update.z[0] != null) {
                    Plotly.update(current_value, update, [0]);
                }
            }
            else {
                console.log("Update type" + plot_type + " not found.");
            }
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
                        const receivedJSON = JSON.parse(this.responseText);
                        if (receivedJSON["0"] !== "__EMPTY")
                            vm.all_projects = receivedJSON;
                        else
                            console.log("No projects found.")
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
                        const receivedJSON = JSON.parse(this.responseText);
                        if (receivedJSON["0"] !== "__EMPTY")
                            vm.all_runs = receivedJSON;
                        else
                            console.log("No runs found.")
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

                        const receivedJSON = JSON.parse(this.responseText);
                        if (receivedJSON["0"] !== "__EMPTY") {
                            vm.current_variables = receivedJSON;
                            vm.run_plots_init = true;
                        }
                        else
                            console.log("No runs found.");
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
                let current_value = this.current_variables[k];
                const plot_type = current_value.split("_")[0];
                if (plot_type === "scalar") {
                    this.show_scalar_plot(current_value);
                }
                else if (plot_type === "heatmap") {
                    this.show_heatmap_plot(current_value);
                }
                else {
                    console.log("Plot type" + plot_type + " not found.");
                }
            }
            this.toggle_refresh();
            return true;
        },
        show_scalar_plot: function(current_value) {
            this.scalar_variable_values[current_value] = {"x": [], "y": []};
            let layout = {
                showlegend: true,
                autosize: true,
                margin: {b: 30, t: 20, l: 50, r: 50},
            };
            let trace = [{
                name: this.extract_correct_name(current_value),  // Remove variable type from its name
                x: this.scalar_variable_values[current_value]["x"],
                y: this.scalar_variable_values[current_value]["y"],
                type: 'scatter',
                line: {shape: "spline", smoothing: this.smoothing_value}
            }];
            Plotly.newPlot(current_value, trace, layout, {displayModeBar: false});
            console.log("Scalar Plot: " + current_value);
        },
        show_heatmap_plot: function(current_value) {
            this.heatmap_variable_values[current_value] = {"vn": [], "z": []};
            let layout = {
                showlegend: true,
                autosize: true,
                margin: {b: 30, t: 20, l: 50, r: 50},
                yaxis: {autorange: 'reversed'},
            };
            let trace = [{
                name: this.extract_correct_name(current_value),  // Remove variable type from its name,
                x: this.heatmap_variable_values[current_value]["x"],
                y: this.heatmap_variable_values[current_value]["y"],
                z: this.heatmap_variable_values[current_value]["z"],
                colorscale: 'YIGnBu',
                type: 'heatmap',
            }];
            Plotly.newPlot(current_value, trace, layout, {displayModeBar: false});
            console.log("Heatmap Plot: " + current_value);
        },
        set_run: function (run_selected) {
            /*
            Updates the current_run variable with the run selected using the dropdown menu.
            Gets the variables that need to plotted and also ensures that the plots are shown.
             */
            this.current_run = run_selected;
            this.get_variables();
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
        show_dashboard_window: function () {
            console.log("show_dashboard_window");
            // Stop refreshing, not using toggle as it messes with the timer and does not stop it.
            clearInterval(this.timer);
            this.refresh_button_text = "Start Refreshing";
            console.log("Refreshing for plots stopped.");
            // Change DOM
            this.current_window = "dashboard";
        },
        show_mouse_over: function (text) {
            document.getElementById(text+"_text").innerHTML = text;
        },
        hide_mouse_over: function (text) {
            document.getElementById(text+"_text").innerHTML = "";
        },
        show_project_management: function () {
            this.showModal = true;  // Display project management modal
        },
        extract_correct_name: function (variable_name) {
            return variable_name.slice(variable_name.indexOf("_")+1);
        },
        isCurrentVariableEmpty: function () {
            return Object.keys(this.current_variables).length < 1;
        },
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

function force() {
    vue_dashboard.set_run(vue_dashboard.current_run);
}
