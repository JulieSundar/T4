// Live-Data ~ MQTT / SocketIO
var socketURL = window.location;
var mqTopic ='gyro';
// Off-line data ~ REst API
var restURL = window.location;
var restEndpoint = 'gpio/12/';
var polling=0; // frequency of polling for tthis chart 0=never
              // display date/time of last measurement

// Chart user params 
var dataSeries = ['X', 'Y', 'Z'];
var chartName='Watch me nene ...';
var renderTarget ='importantchart';

// Action params - activate and manage measurements here
var startMeasure = '';  // RestAPI call to start measuring
var stopMeasure = '';   // controlled by timing if <>0 or to overrule measurement
var measureTime = 0;   // Timing in seconds for measurement 0=unlimited
                        // ### ToDo: add spakline chart during measuring -> chart + target


// (maybe in a JSON string?? to pull into configurator)
// To DO: Load chart, data and widtget configs from cookie or back-end
//widget.params={socketURL:"", mqTopic:"" };

// start loading chart ### load_widget()
$(function () {
//function load_live_chart(tile, div, params) {
  console.log("load_live_chart");
  var chart,
    // series defaults (in case no connections)
    categories = ['Categorie 1', 'Categorie 2', 'Categorie 3', 'Categorie 4', 'Categorie 5','Categorie 6', 'Categorie 7', 'Categorie 8', 'Categorie 9', 'Categorie 10', 'Categorie 11', 'Categorie 12', 'Categorie 13', 'Categorie 14', 'Categorie 15', 'Categorie 16', 'Categorie 17', 'Categorie 18', 'Categorie 19','Categorie 20', 'Categorie 21','Categorie 22', 'Categorie 23', 'Categorie 24', 'Categorie 25', 'Categorie 26', 'Categorie 27', 'Categorie 28', 'Categorie 29', 'Categorie 30'],
    serie1 = [0,1,2,3,4,5],
    serie2 = [0,1,2,3,4,5];

    // Setup the chart 
  chart = new Highcharts.Chart({
    chart: {
      renderTo: renderTarget,
      type: 'column',
      backgroundColor: 'transparent',
      height: 140,
      marginLeft: 3,
      marginRight: 3,
      marginBottom: 0,
      marginTop: 0
    },
    title: {
      text: chartName
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
        text: null,
      },
    },
    series: [{
      name: chartName,
      color: '#f1d',
      type: 'line',
      data: serie1
    }, {
      name: 'Gyro-Y',
      color: '#fff',
      type: 'line',
      data: serie2
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
  });
  // End setup chart


  // Get Data for chart
  // Live data from mqtt over socket
  var socket = io.connect(socketURL);

  // Subscribe to MQTT topic
  socket.emit('subscribe',{topic:mqTopic});

  // 1. open socket & listen to MQTT topic messages
  socket.on('connect', function () {
    socket.on('mqtt', function (msg) {
      //console.log(msg);
      if (msg.topic==mqTopic) {
        $(".graph-info-big").text(mqTopic);

        // any new gyro values coming in will be added to the chart array
        var data = JSON.parse(msg.payload);
        $(".graph-info-small").text(data.X);
        // Series Parameterized
        // switch for Live or Off-line data
        // if chart in live mode push new data to array else use the whole series
        // if (chart=live){

        //} ELSE{
        //  chart.series[i]=data.dataSeries(i)
        //}
        //for each dataItem in array dataSeries //([X, Y, Z])
          //chart.series[i].addPoint(parseFloat(data.[dataItems[i]]), true, true);

          chart.series[0].addPoint(parseFloat(data.Y), true, true);
          chart.series[1].addPoint(parseFloat(data.Z), true, true);
        //endfor
        //chart.serie[2].addPoint(parseFloat(data.Z), true, true);
        
        //chart.series[0].addPoint(parseFloat(msg.payload), true, true);
        // cleanup old data from array (>1000 elements???)



      }      
    });
  });
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
  

});
