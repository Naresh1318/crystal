    // Plotting parameters
    // TODO: Get this value from the user
    var refresh_time = 500; // Refresh time in ms


    {% for v_n in variable_names %}
    var trace_%%v_n[0] %% = [{
        x: [],
        y: [],
        type: 'scatter'
    }];

    Plotly.newPlot('%%v_n[0]%%', trace_%%v_n[0]%%);
    {% endfor %}


    function updateGraphs() {
        var xmlhhtp = new XMLHttpRequest(),
            method = "GET",
            url = "%%url_for('update')%%";

        xmlhhtp.open(method, url, true);
        xmlhhtp.onreadystatechange = function () {
            if (this.readyState === XMLHttpRequest.DONE && this.status === 200){
                console.log(JSON.parse(xmlhhtp.responseText));

                var receivedJSON = JSON.parse(xmlhhtp.responseText);

                {% for v_n in variable_names %}
                var update_%%v_n[0]%% = {
                    x:  [receivedJSON['%%v_n[0]%%']['x']],
                    y: [receivedJSON['%%v_n[0]%%']['y']]
                };
                console.log(receivedJSON['%%v_n[0]%%']['x']);
                Plotly.extendTraces('%%v_n[0]%%', update_%%v_n[0]%%, [0]);
                {% endfor %}
            }
        };
        xmlhhtp.send()
    }

    // TODO: Do something that know when it hasn't received anything when you send a request.
    var timer = setInterval(function () {
        updateGraphs();
    }, refresh_time);