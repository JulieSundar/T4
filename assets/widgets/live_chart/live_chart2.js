// start loading 
function load_live_chart(title,div, params) {
	console.log("load_live_chart : " +  title + " to <DIV>" + div + "</DIV>");
	//Data Params / defaults (can be overwritten on instantiation / restore config-time)
	// Live-Data ~ MQTT / SocketIO
	var socketURL = window.location.host;
	var mqTopic ='gyro';
	var params={ 
	    // ### Data Params ### (add style elements under _name these will only be used for styling )
	    data: {
	      feedSelect: 'auto', // dropdown from auto, socket, if Live feed available use that, else use REST
	      // Live-Data ~ MQTT / SocketIO
	      socketURL : '%window.location.host%', //  %params% will be run-time evaluated and replaced with result string
	      mqTopic :'gyro',
	      // Off-line data ~ REst API    
	      restURL : "%window.location.host%/gpio/12/",
	      restPolling:3000,
	      dataSeries:['X', 'Y', 'Z'],
	      programmability:{
	        framework: 'none',
	        jQuery: 'false',
	      }
	    },        
	    chart: {
	      renderTo: '%div%',
	      type: 'column',
	      backgroundColor: 'transparent', //params.backgroundColor||defparams.backgroundColor
	      height: 140,
	      marginLeft: 3,
	      marginRight: 3,
	      marginBottom: 0,
	      marginTop: 0,
	    title: {
	      text: '%title%'
	    },
	    xAxis: {
	      lineWidth: 0,
	      tickWidth: 0,
	      labels: { 
	      enabled: false 
	      },
	      categories: '%categories%'
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
	      name: "yeah waevah",
	      color: '#f00',
	      type: 'line',
	      data: '%serie1%'
	    }, {
	      name: 'Gyro-Y',
	      color: '#fff',
	      type: 'line',
	      data: '%serie2%'
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
	      lineWidth: 3
	      }
	    },

	    tooltip: { 
	      enabled: false
	    }
	  },
	};


	var params={ 
		// ### Data Params ###
		feedSelect: 'auto', // dropdown from auto, socket, if Live feed available use that, else use REST
		// Live-Data ~ MQTT / SocketIO
		socketURL : '%window.location.host%', //  %params% will be run-time evaluated and replaced with result string
		mqTopic :'gyro',
		// Off-line data ~ REst API    
		restURL : "%window.location.host%/gpio/12/",
		restPolling:3000,
		dataSeries:['X', 'Y', 'Z'], //?? check data-feeds/chart-data wire-up...
		// ## CHART Editable options
		tooltip: false,
		/* text this part
		series: [{
			name: "yeah waevah",
			color: '#f00',
			type: 'line',
			data: serie1
		}, {
			name: 'Gyro-Y',
			color: '#fff',
			type: 'line',
			data: serie2
		}],
		*/
	};
	
	// This is the metadata object for jqPropertyGrid that describes the target object properties (optional)
	var jqmeta = {
        // ### Data Params ### (add style elements under _name these will only be used for styling )
        data: {
          feedSelect: {type: 'options', options: ['auto', {text:'Auto-select', value: 'auto'}, {text:'Live ~ MQTT/Socket', value: 'socket'},{text:'REST API', value: 'rest'}], description: 'Select from type of input for widget (auto precedes socket over Rest'},
          socketURL : {description: 'live data socket URL env variables allowed eg %hostname%' },
          mqTopic :{description: 'Message Q Topic' },  
          restURL : {description: 'Offline data Rest URL env variables allowed eg %hostname%' },
          restPolling:{description: 'REST polling (ms)' },
          dataSeries:{description: 'Array of data-streams/series' },
          programmability:{
            framework: {type: 'options', options: ['None', {text:'AngularJS', value: 'angular'}, {text:'Backbone.js', value: 'backbone'}], description: 'Whether to include any additional framework'},
            jQuery: {description: 'Whether or not to include jQuery on the page' },
          }
        },        
        chart: {
          renderTo: '',
          type: 'column',
          backgroundColor: {name: 'bg color', type: 'color', options: { preferredFormat: 'hex' }},
          height: {type: 'number', options: { min: 0, step: 1 }},
          marginLeft: {type: 'number', options: { min: 0, max: 100, step: 1 }},
          marginRight: {type: 'number', options: { min: 0, max: 100, step: 1 }},
          marginBottom: {type: 'number', options: { min: 0, max: 100, step: 1 }},
          marginTop: {type: 'number', options: { min: 0, max: 100, step: 1 }},
        title: {
          text: ''
        },
        xAxis: {
          lineWidth: {type: 'number', options: { min: 1, max: 20, step: 1 }},
          tickWidth: {type: 'number', options: { min: 1, max: 20, step: 1 }},
          labels: { 
          enabled: false 
          },
          categories: ''
        },
        yAxis: {
          labels: { 
          enabled: false 
          },
          gridLineWidth: {type: 'number', options: { min: 1, max: 20, step: 1 }},
          title: {
          text: null
          },
        },
        series: [{
          name: '',
          color: {type: 'color', options: { preferredFormat: 'hex' }},
          type: 'line', // ###JULIE check for the HighCharts options and make a dropdown
          data: ''
        }, {
          name: '',
          color: {type: 'color', options: { preferredFormat: 'hex' }},
          type: 'line',
          data: ''
        }],
        credits: { 
          enabled: false 
        },
        legend: { 
          enabled: false 
        },
        plotOptions: {
          column: {
          borderWidth: {type: 'number', options: { min: 1, max: 20, step: 1 }},
          color: {type: 'color', options: { preferredFormat: 'hex' }},
          shadow: false
          },
          line: {
          marker: { 
            enabled: false 
          },
          lineWidth: {type: 'number', options: { min: 1, max: 20, step: 1 }}
          }
        },

        tooltip: { 
          enabled: false
        }
      },
    };


	var chart,
    // series defaults (in case no connections)
    categories = ['Categorie 1', 'Categorie 2', 'Categorie 3', 'Categorie 4', 'Categorie 5','Categorie 6', 'Categorie 7', 'Categorie 8', 'Categorie 9', 'Categorie 10', 'Categorie 11', 'Categorie 12', 'Categorie 13', 'Categorie 14', 'Categorie 15', 'Categorie 16', 'Categorie 17', 'Categorie 18', 'Categorie 19','Categorie 20', 'Categorie 21','Categorie 22', 'Categorie 23', 'Categorie 24', 'Categorie 25', 'Categorie 26', 'Categorie 27', 'Categorie 28', 'Categorie 29', 'Categorie 30'],
    serie1 = [0,1,2,3,4,5],
    serie2 = [0,1,2,3,4,5];

    // Setup the chart 
    console.log(params[chart]);
	chart = new Highcharts.Chart(params[chart]){};
	// End setup chart


  // Get Data for chart
  // Live data from mqtt over socket
  //Check for existing socket and reuse
  var socket = io.connect((params[data].socketURL=='hostURL'||'host') ? window.location.host : params.socketURL);

  // Subscribe to MQTT topic
  socket.emit('subscribe',{topic: params[data].mqTopic});

  // 1. open socket & listen to MQTT topic messages
  socket.on('connect', function () {
    socket.on('mqtt', function (msg) {
		//console.log(msg);
		if (msg.topic==params[data].mqTopic) {
			//$(".graph-info-big").text(mqTopic);

			// any new gyro values coming in will be added to the chart array
			var data = JSON.parse(msg.payload);
			//$(".graph-info-small").text(data.X);
			// Series Parameterized
			// switch for Live or Off-line data
			// if chart in live mode push new data to array else use the whole series

			//  chart.series[i]=data.dataSeries(i)

			//for each dataItem in array dataSeries //([X, Y, Z])
			//chart.series[i].addPoint(parseFloat(data.[dataItems[i]]), true, true);
			// ### TODO .. wire-up??
			chart.series[0].addPoint(parseFloat(data.Y), true, true);
			chart.series[1].addPoint(parseFloat(data.Z), true, true);
			//endfor
			//chart.serie[2].addPoint(parseFloat(data.Z), true, true);

			//chart.series[0].addPoint(parseFloat(msg.payload), true, true);
			// cleanup old data from array (>1000 elements???)
		}      
    })
  })
}

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

