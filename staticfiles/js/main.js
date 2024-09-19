(function ($) {

  "use strict";

  var fullHeight = function () {

    $('.js-fullheight').css('height', $(window).height());
    $(window).resize(function () {
      $('.js-fullheight').css('height', $(window).height());
    });

  };
  fullHeight();

  $('#sidebarCollapse').on('click', function () {
    $('#sidebar').toggleClass('active');
  });

})(jQuery);


google.load("visualization", "1", { packages: ["corechart"] });
google.setOnLoadCallback(drawCharts);

function drawCharts() {
  fetch('/api/sales-data/')
    .then(response => response.json())
    .then(data => {
      var chartData = new google.visualization.DataTable();
      chartData.addColumn('string', 'Date');
      chartData.addColumn('number', 'Amount');

      data.forEach(item => {
        chartData.addRow([new Date(item.date).toLocaleDateString(), item.amount]);
      });

      var barOptions = {
        focusTarget: 'category',
        backgroundColor: 'transparent',
        colors: ['#FB9678', '#03C9D7'],
        fontName: 'Open Sans',
        chartArea: {
          left: 50,
          top: 10,
          width: '75%',
          height: '85%',
          borderRadius: "20%"
        },
        bar: {
          groupWidth: '80%'
        },
        hAxis: {
          textStyle: {
            fontSize: 11
          }
        },
        vAxis: {
          minValue: 0,
          baselineColor: '#DDD',
          gridlines: {
            color: '#DDD',
            count: 4
          },
          textStyle: {
            fontSize: 11
          }
        },
        legend: {
          position: 'bottom',
          textStyle: {
            fontSize: 12
          }
        },
        animation: {
          duration: 1200,
          easing: 'out',
          startup: true
        }
      };

      var barChart = new google.visualization.ColumnChart(document.getElementById('bar-chart'));
      barChart.draw(chartData, barOptions);
    })
    .catch(error => console.error('Error fetching sales data:', error));
}

  // BEGIN LINE GRAPH

  function randomNumber(base, step) {
    return Math.floor((Math.random() * step) + base);
  }
  function createData(year, start1, start2, step, offset) {
    var ar = [];
    for (var i = 0; i < 12; i++) {
      ar.push([new Date(year, i), randomNumber(start1, step) + offset, randomNumber(start2, step) + offset]);
    }
    return ar;
  }
  var randomLineData = [
    ['Year', 'Page Views', 'Unique Views']
  ];
  for (var x = 0; x < 7; x++) {
    var newYear = createData(2007 + x, 10000, 5000, 4000, 800 * Math.pow(x, 2));
    for (var n = 0; n < 12; n++) {
      randomLineData.push(newYear.shift());
    }
  }
  var lineData = google.visualization.arrayToDataTable(randomLineData);

  /*
  var animLineData = [
    ['Year', 'Page Views', 'Unique Views']
  ];
  for (var x = 0; x < 7; x++) {
    var zeroYear = createData(2007+x, 0, 0, 0, 0);
    for (var n = 0; n < 12; n++) {
      animLineData.push(zeroYear.shift());
    }
  }
  var zeroLineData = google.visualization.arrayToDataTable(animLineData);
  */

  var lineOptions = {
    backgroundColor: 'transparent',
    colors: ['#FB9678', '#FB9678'],
    fontName: 'Open Sans',
    focusTarget: 'category',
    chartArea: {
      left: 50,
      top: 10,
      width: '100%',
      height: '70%'
    },
    hAxis: {
      //showTextEvery: 12,
      textStyle: {
        fontSize: 11
      },
      baselineColor: 'transparent',
      gridlines: {
        color: 'transparent'
      }
    },
    vAxis: {
      minValue: 0,
      maxValue: 50000,
      baselineColor: '#FB9678',
      gridlines: {
        color: '#FB9678',
        count: 4
      },
      textStyle: {
        fontSize: 11
      }
    },
    legend: {
      position: 'bottom',
      textStyle: {
        fontSize: 12
      }
    },
    animation: {
      duration: 1200,
      easing: 'out',
      startup: true
    }
  };

  var lineChart = new google.visualization.LineChart(document.getElementById('line-chart'));
  //lineChart.draw(zeroLineData, lineOptions);
  lineChart.draw(lineData, lineOptions);

  // BEGIN PIE CHART

  // pie chart data
  var pieData = google.visualization.arrayToDataTable([
    ['Country', 'Page Hits'],
    ['USA', 7242],
    ['Canada', 4563],
    ['Mexico', 1345],
    ['Sweden', 946],
    ['Germany', 2150]
  ]);
  // pie chart options
  var pieOptions = {
    backgroundColor: 'transparent',
    pieHole: 0.4,

    pieSliceText: 'value',
    tooltip: {
      text: 'percentage'
    },
    fontName: 'Open Sans',
    chartArea: {
      width: '100%',
      height: '94%'
    },
    legend: {
      textStyle: {
        fontSize: 13
      }
    }
  };
  // draw pie chart
  var pieChart = new google.visualization.PieChart(document.getElementById('pie-chart'));
  pieChart.draw(pieData, pieOptions);



var data = [
  { y: '2014', a: 50, b: 90 },
  { y: '2015', a: 65, b: 75 },
  { y: '2016', a: 50, b: 50 },
  { y: '2017', a: 75, b: 60 },
  { y: '2018', a: 80, b: 65 },
  { y: '2019', a: 90, b: 70 },
  { y: '2020', a: 100, b: 75 },
  { y: '2021', a: 115, b: 75 },
  { y: '2022', a: 120, b: 85 },
  { y: '2023', a: 145, b: 85 },
  { y: '2024', a: 160, b: 95 }
],
  config = {
    data: data,
    xkey: 'y',
    ykeys: ['a', 'b'],
    labels: ['Total Income', 'Total Outcome'],
    fillOpacity: 0.6,
    hideHover: 'auto',
    behaveLikeLine: true,
    resize: true,
    pointFillColors: ['#ffffff'],
    pointStrokeColors: ['black'],
    lineColors: ['gray', 'red']
  };
config.element = 'area-chart';
Morris.Area(config);
config.element = 'line-chart';
Morris.Line(config);
config.element = 'bar-chart';
Morris.Bar(config);
config.element = 'stacked';
config.stacked = true;
Morris.Bar(config);
Morris.Donut({
  element: 'pie-chart',
  data: [
    { label: "Friends", value: 30 },
    { label: "Allies", value: 15 },
    { label: "Enemies", value: 45 },
    { label: "Neutral", value: 10 }
  ]
});

function handleSubItemClick(submenuId, clickedItem) {
  const submenuItems = document.querySelectorAll(`#${submenuId} li`);
  submenuItems.forEach(item => {
    if (item.classList.contains('active-submenu')) {
      item.classList.remove('active-submenu');
    }
  });

  // Add 'active-submenu' class to the clicked submenu item
  clickedItem.classList.add('active-submenu');
}
