// start loading 
function load_live_chart(title, div, par){
    console.log("load_live_chart : " + title + " to <div>" + div + "</div>");
    var chart;
    // series defaults (in case no connections)
    var categories = ['Categorie 1', 'Categorie 2', 'Categorie 3', 'Categorie 4', 'Categorie 5', 'Categorie 6', 'Categorie 7', 'Categorie 8', 'Categorie 9', 'Categorie 10', 'Categorie 11', 'Categorie 12', 'Categorie 13', 'Categorie 14', 'Categorie 15', 'Categorie 16', 'Categorie 17', 'Categorie 18', 'Categorie 19', 'Categorie 20', 'Categorie 21', 'Categorie 22', 'Categorie 23', 'Categorie 24', 'Categorie 25', 'Categorie 26', 'Categorie 27', 'Categorie 28', 'Categorie 29', 'Categorie 30'];

    // JSON Utility functions to flatten Object
    JSON.flatten = function (data) {
        var result = {};
        function recurse(cur, prop) {
            if (Object(cur) !== cur) {
                result[prop] = cur;
            } else if (Array.isArray(cur)) {
                for (var i = 0, l = cur.length; i < l; i++)
                // ###TB recurse(cur[i], prop + "[" + i + "]");
                recurse(cur[i], prop + ".[" + i + "]");
                if (l == 0) result[prop] = [];
            } else {
                var isEmpty = true;
                for (var p in cur) {
                    isEmpty = false;
                    recurse(cur[p], prop ? prop + "." + p : p);
                }
                if (isEmpty && prop) result[prop] = {};
            }
        }
        recurse(data, "");
        return result;
    };

    JSON.unflatten = function (data) {
        "use strict";
        if (Object(data) !== data || Array.isArray(data)) return data;
        var regex = /\.?([^.\[\]]+)|\[(\d+)\]/g,
            resultholder = {};
        for (var p in data) {
            var cur = resultholder,
                prop = "",
                m;
            while (m = regex.exec(p)) {
                cur = cur[prop] || (cur[prop] = (m[2] ? [] : {}));
                prop = m[2] || m[1];
            }
            cur[prop] = data[p];
        }
        return resultholder[""] || resultholder;
    };

    function parseEnvVars(str) {
        // function parses and updates app/system environment variables eg. %windows%
        // ### TODO Make fit for embedded code/functions to instantiate them at run-time too
        //console.log("parsing: " + str)
        var str_array = str.split(";");

        var new_path = '';
        for (var x = 0; x < str_array.length; x++) {
            // if a %keyword% detected , parse and handle/evaluate
            if (str_array[x].match(/(.*)(%.+%)(.*)/)) {
                str_array[x].match(/(.*)(%.+%)(.*)/);
                var pre_variable = RegExp.$1;
                var env_variable = RegExp.$2.slice(1, -1);
                var post_variable = RegExp.$3;

                // if variable doesn't exist just return the string
                new_path += pre_variable + ((x > 0) ? ";" : "") + eval(env_variable) + post_variable;
            } else {
                // no % detected, just add the string sequence as is
                new_path += ((x > 0) ? ";" : "") + str_array[x];
            }
        }
        return new_path;
    }

    // Parse EnvVariables & Functions in object and inject/replace with value/run-time values
    // Optionally If parameter NOT entered use the default value ()
    function parseParamObj(defObj,optObj) {
        // Flatten def & par Objects, 
        // 1. Merge/insert keys from default retParam Object
        retObj= $.extend(true,defObj,optObj);
        var flatObj = JSON.flatten(retObj);
        // 2. find envVars and replace
        for (prop in flatObj) {
            // if key value contains '%' replace with evaluated code
            //console.log("parsing: " + prop + " : " + flatObj[prop]);
            if ((flatObj[prop]+' ').match(/(%.+%)/)) {
                // parse & replace Env Variables
                flatObj[prop] = parseEnvVars(flatObj[prop]);
                //console.log(prop + ' is updated : ' + flatObj[prop]);
            }
        }
        //console.log(JSON.unflatten(flatObj));
        retObj=JSON.unflatten(flatObj);
        console.log(retObj);
        return retObj;
    }
    // ##### DEFAULT PARAMS HERE #####
    // If no parameter object passed with chart call use the default set provided here
    // or if the user resets config back to default in configurator 
    var defParams = {
        data: {
            feedSelect: 'auto', // dropdown from auto, socket, if Live feed available use that, else use REST
            // Live-Data ~ MQTT / SocketIO
            socketURL: '%window.location.host%', //  %params% will be run-time evaluated and replaced with result string
            mqTopic: 'none',
            // Off-line data ~ REst API    
            restURL: "%window.location.host%",
            restPolling: 3000, // also wait for this time to scan for live feed data
            dataSeries: ['Y', 'Z'],
            refreshRate: 10,   // after how many data points to redraw canvas/chart etc
            persistPoints:20  // How many data-points to persist (ongoing/per session)
        },
        // highCharts config here       
        chart: {           
            rangeSelector: {
                selected: 1
            },
            renderTo: div,
            type: 'column',
            backgroundColor: 'fff',
            height: 140,
            marginLeft: 3,
            marginRight: 3,
            marginBottom: 0,
            marginTop: 0,
            title: {
                text: title
            },
            xAxis: {
                lineWidth: 0,
                tickWidth: 0,
                labels: {
                    enabled: false
                },
                categories: categories
            },
            yAxis: {
                labels: {
                    enabled: false
                },
                gridLineWidth: 0,
                title: {
                    text: null
                },
            },
            series: [{
                name: "Gyro-Y",
                color: '#00f',
                type: 'spline',
                data: []
            }, {
                name: 'Gyro-Z',
                color: '#0f0',
                type: 'spline',
                data: []
            },
            {
               name: 'Shift',
               color: '#f00',
               type: 'line',
               data: []
           }],
            credits: {
                enabled: false
            },
            legend: {
                enabled: false
            },
            plotOptions: {
                column: {
                    borderWidth: 0,
                    color: '#b2c831',
                    shadow: false
                },
                line: {
                    marker: {
                        enabled: false
                    },
                    lineWidth: 1
                }
            },

            tooltip: {
                enabled: false
            },
        }
    }

    // ##### jqPropertygrid Meta #####
    // This is the metadata object for jqPropertyGrid that describes the target object properties (optional)
    var jqmeta = {
        data: {
            feedSelect: {
                type: 'options',
                options: ['auto', {
                    text: 'Auto-select',
                    value: 'auto'
                }, {
                    text: 'Live ~ MQTT/Socket',
                    value: 'socket'
                }, {
                    text: 'REST API',
                    value: 'rest'
                }],
                description: 'Select from type of input for widget (auto precedes socket over Rest'
            },
            socketURL: {
                description: 'live data socket URL env variables allowed eg %hostname%'
            },
            mqTopic: {
                description: 'Message Q Topic'
            },
            restURL: {
                description: 'Offline data Rest URL env variables allowed eg %hostname%'
            },
            restPolling: {
                description: 'REST polling (ms)'
            },
            dataSeries: {
                description: 'Array of data-streams/series'
            },
            programmability: {
                framework: {
                    type: 'options',
                    options: ['None', {
                        text: 'AngularJS',
                        value: 'angular'
                    }, {
                        text: 'Backbone.js',
                        value: 'backbone'
                    }],
                    description: 'Whether to include any additional framework'
                },
                jQuery: {
                    description: 'Whether or not to include jQuery on the page'
                },
            }
        },
        chart:{
            renderTo: '',
            type: 'column',
            backgroundColor: {
                name: 'bg color',
                type: 'color',
                options: {
                    preferredFormat: 'hex'
                }
            },
            height: {
                type: 'number',
                options: {
                    min: 0,
                    step: 1
                }
            },
            marginLeft: {
                type: 'number',
                options: {
                    min: 0,
                    max: 100,
                    step: 1
                }
            },
            marginRight: {
                type: 'number',
                options: {
                    min: 0,
                    max: 100,
                    step: 1
                }
            },
            marginBottom: {
                type: 'number',
                options: {
                    min: 0,
                    max: 100,
                    step: 1
                }
            },
            marginTop: {
                type: 'number',
                options: {
                    min: 0,
                    max: 100,
                    step: 1
                }
            },
            title: {
                text: 'test'
            },
            xAxis: {
                lineWidth: {
                    type: 'number',
                    options: {
                        min: 1,
                        max: 20,
                        step: 1
                    }
                },
                tickWidth: {
                    type: 'number',
                    options: {
                        min: 1,
                        max: 20,
                        step: 1
                    }
                },
                labels: {
                    enabled: false
                },
                categories: ''
            },
            yAxis: {
                labels: {
                    enabled: false
                },
                gridLineWidth: {
                    type: 'number',
                    options: {
                        min: 1,
                        max: 20,
                        step: 1
                    }
                },
                title: {
                    text: null
                },
            },
            series: [{
                name: '',
                color: {
                    type: 'color',
                    options: {
                        preferredFormat: 'hex'
                    }
                },
                type: 'line', // ###JULIE check for the HighCharts options and make a dropdown
                data: ''
            }, {
                name: '',
                color: {
                    type: 'color',
                    options: {
                        preferredFormat: 'hex'
                    }
                },
                type: 'line',
                data: ''
            }],
            credits: {
                enabled: false
            },
            legend: {
                enabled:false
            },
            plotOptions: {
                column: {
                    borderWidth: {
                        type: 'number',
                        options: {
                            min: 1,
                            max: 20,
                            step: 1
                        }
                    },
                    color: {
                        type: 'color',
                        options: {
                            preferredFormat: 'hex'
                        }
                    },
                    shadow: 0
                },
                line: {
                    marker: {
                        enabled: false
                    },
                    lineWidth: {
                        type: 'number',
                        options: {
                            min: 1,
                            max: 20,
                            step: 1
                        }
                    }
                }
            },
            tooltip: {
                enabled: true
            }                    
        }
    };
    
    // ##### CHART DATA #####
    function fetch_data(){
        // TODOS
        // ### MQTT DATA ###Live data from mqtt over socket
        // ### Check for existing socket and reuse
        // ### Use socketIO rooms option to decrease traffic handling
        // ### switch for Live or Off-line data

        var chart = $('#'+div).highcharts();
        // PARAMETERIZE THIS SECTION!!!
        // for each series create an item in array
        // for each in params.series[] do append to array
        var series=[ chart.series[0],chart.series[1],chart.series[2]];

        // Try to run socket .. else fall-back to API
        //console.log("socket:" + params.data.socketURL);
        var socket = io.connect((params.data.socketURL)); 
        // Subscribe to MQTT topic
        socket.emit('subscribe', {
            topic: params.data.mqTopic
        });

        // 1. open socket & listen to MQTT topic messages
        // display refresh rate (points)
        var i = 0;
        socket.on('connect', function() {
            chart.redraw();
            socket.on('mqtt', function(msg) {
                //console.log(msg);
                if (msg.topic == params.data.mqTopic) {
                    // any new values coming in will be added to the chart array
                    var data = JSON.parse(msg.payload);

                    // if chart in live mode push new data to array else use the whole series
                    shift = chart.series[0].length > (params.data.persistPoints || 10000) ;
                    console.log(chart.series[0].length);
                    // use FOR loop here
                    series[0].addPoint(parseFloat(data.Y), false, shift);
                    series[1].addPoint(parseFloat(data.Z), false, shift);
                    //series[2].addPoint(parseFloat(shift)*parseFloat(data.Z)*1.5, false, shift);
                    // Update frequency (100 points / parameterize sec par: refreshCount)
                    // MAYBE OPTIONALLY USE TIME FOR REFRESH??
                    if (i > params.data.refreshRate){ 
                        chart.redraw();
                        i=0;
                    }else{
                        i++
                    };
                }
            })
        });
    };

    // ##### SETUP CHART #####
    // (IMPORTANT ADD{} behind the chart object for the Live Data to be injected!!)
    // Merge def and call params (add missing/default keys)
    var params=parseParamObj(defParams,par);
    console.log(params);
    // Instantiate chart here
    chart = $('#'+div).highcharts('StockChart',params['chart'] );
    // start data
    fetch_data();

    // hook the settings modal??


};


/*
  // 2. Connect to Rest/API and capture data into array
  $.ajax({
    type: "GET",
    dataType: "jsonp",
    url: hostURL +'/'+ restEndpoint,

    success: function (data) {
      
      data = JSON.parse(data.Result).Table;
      
      var series = [{
        type: 'area',
        name: 'Rate to USD',
        data: [] // will added to in the following for-loop
      }, {
        type: 'line',
        name: 'Rate to SRD',
        data: []
      }];
      
      for(var i = 0, l = data.length; i < l; ++i) {
        var d = ("" + data[i].date_time).split(",");
        if(d.length >= 7) {
          series[0].data.push([
            Date.UTC(d[0], d[1], d[2], d[3], d[4], d[5], d[6]),
            parseFloat(data[i].rate_toDollar),
            data[i].notes
          ]);
          series[1].data.push([
            Date.UTC(d[0], d[1], d[2], d[3], d[4], d[5], d[6]),
            parseFloat(data[i].rate),
            data[i]
          ]);
        }
      }
*/
