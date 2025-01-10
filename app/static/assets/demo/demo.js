type = ['primary', 'info', 'success', 'warning', 'danger'];

demo = {
  initPickColor: function() {
    $('.pick-class-label').click(function() {
      var new_class = $(this).attr('new-class');
      var old_class = $('#display-buttons').attr('data-class');
      var display_div = $('#display-buttons');
      if (display_div.length) {
        var display_buttons = display_div.find('.btn');
        display_buttons.removeClass(old_class);
        display_buttons.addClass(new_class);
        display_div.attr('data-class', new_class);
      }
    });
  },

  initDocChart: function() {
    chartColor = "#FFFFFF";

    // General configuration for the charts with Line gradientStroke
    gradientChartOptionsConfiguration = {
      maintainAspectRatio: false,
      legend: {
        display: false
      },
      tooltips: {
        bodySpacing: 4,
        mode: "nearest",
        intersect: 0,
        position: "nearest",
        xPadding: 10,
        yPadding: 10,
        caretPadding: 10
      },
      responsive: true,
      scales: {
        yAxes: [{
          display: 0,
          gridLines: 0,
          ticks: {
            display: false
          },
          gridLines: {
            zeroLineColor: "transparent",
            drawTicks: false,
            display: false,
            drawBorder: false
          }
        }],
        xAxes: [{
          display: 0,
          gridLines: 0,
          ticks: {
            display: false
          },
          gridLines: {
            zeroLineColor: "transparent",
            drawTicks: false,
            display: false,
            drawBorder: false
          }
        }]
      },
      layout: {
        padding: {
          left: 0,
          right: 0,
          top: 15,
          bottom: 15
        }
      }
    };

    ctx = document.getElementById('lineChartExample').getContext("2d");

    gradientStroke = ctx.createLinearGradient(500, 0, 100, 0);
    gradientStroke.addColorStop(0, '#80b6f4');
    gradientStroke.addColorStop(1, chartColor);

    gradientFill = ctx.createLinearGradient(0, 170, 0, 50);
    gradientFill.addColorStop(0, "rgba(128, 182, 244, 0)");
    gradientFill.addColorStop(1, "rgba(249, 99, 59, 0.40)");

    myChart = new Chart(ctx, {
      type: 'line',
      responsive: true,
      data: {
        labels: ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
        datasets: [{
          label: "Active Users",
          borderColor: "#f96332",
          pointBorderColor: "#FFF",
          pointBackgroundColor: "#f96332",
          pointBorderWidth: 2,
          pointHoverRadius: 4,
          pointHoverBorderWidth: 1,
          pointRadius: 4,
          fill: true,
          backgroundColor: gradientFill,
          borderWidth: 2,
          data: [542, 480, 430, 550, 530, 453, 380, 434, 568, 610, 700, 630]
        }]
      },
      options: gradientChartOptionsConfiguration
    });
  },

  initDashboardPageCharts: function() {

    gradientChartOptionsConfigurationWithTooltipBlue = {
      maintainAspectRatio: false,
      legend: {
        display: false
      },

      tooltips: {
        backgroundColor: '#f5f5f5',
        titleFontColor: '#333',
        bodyFontColor: '#666',
        bodySpacing: 4,
        xPadding: 12,
        mode: "nearest",
        intersect: 0,
        position: "nearest"
      },
      responsive: true,
      scales: {
        yAxes: [{
          barPercentage: 1.6,
          gridLines: {
            drawBorder: false,
            color: 'rgba(29,140,248,0.0)',
            zeroLineColor: "transparent",
          },
          ticks: {
            suggestedMin: 60,
            suggestedMax: 125,
            padding: 20,
            fontColor: "#2380f7"
          }
        }],

        xAxes: [{
          barPercentage: 1.6,
          gridLines: {
            drawBorder: false,
            color: 'rgba(29,140,248,0.1)',
            zeroLineColor: "transparent",
          },
          ticks: {
            padding: 20,
            fontColor: "#2380f7"
          }
        }]
      }
    };

    gradientChartOptionsConfigurationWithTooltipPurple = {
      maintainAspectRatio: false,
      legend: {
        display: false
      },

      tooltips: {
        backgroundColor: '#f5f5f5',
        titleFontColor: '#333',
        bodyFontColor: '#666',
        bodySpacing: 4,
        xPadding: 12,
        mode: "nearest",
        intersect: 0,
        position: "nearest"
      },
      responsive: true,
      scales: {
        yAxes: [{
          barPercentage: 1.6,
          gridLines: {
            drawBorder: false,
            color: 'rgba(29,140,248,0.0)',
            zeroLineColor: "transparent",
          },
          ticks: {
            suggestedMin: 60,
            suggestedMax: 125,
            padding: 20,
            fontColor: "#9a9a9a"
          }
        }],

        xAxes: [{
          barPercentage: 1.6,
          gridLines: {
            drawBorder: false,
            color: 'rgba(225,78,202,0.1)',
            zeroLineColor: "transparent",
          },
          ticks: {
            padding: 20,
            fontColor: "#9a9a9a"
          }
        }]
      }
    };

    gradientChartOptionsConfigurationWithTooltipOrange = {
      maintainAspectRatio: false,
      legend: {
        display: false
      },

      tooltips: {
        backgroundColor: '#f5f5f5',
        titleFontColor: '#333',
        bodyFontColor: '#666',
        bodySpacing: 4,
        xPadding: 12,
        mode: "nearest",
        intersect: 0,
        position: "nearest"
      },
      responsive: true,
      scales: {
        yAxes: [{
          barPercentage: 1.6,
          gridLines: {
            drawBorder: false,
            color: 'rgba(29,140,248,0.0)',
            zeroLineColor: "transparent",
          },
          ticks: {
            suggestedMin: 50,
            suggestedMax: 110,
            padding: 20,
            fontColor: "#ff8a76"
          }
        }],

        xAxes: [{
          barPercentage: 1.6,
          gridLines: {
            drawBorder: false,
            color: 'rgba(220,53,69,0.1)',
            zeroLineColor: "transparent",
          },
          ticks: {
            padding: 20,
            fontColor: "#ff8a76"
          }
        }]
      }
    };

    gradientChartOptionsConfigurationWithTooltipGreen = {
      maintainAspectRatio: false,
      legend: {
        display: false
      },

      tooltips: {
        backgroundColor: '#f5f5f5',
        titleFontColor: '#333',
        bodyFontColor: '#666',
        bodySpacing: 4,
        xPadding: 12,
        mode: "nearest",
        intersect: 0,
        position: "nearest"
      },
      responsive: true,
      scales: {
        yAxes: [{
          barPercentage: 1.6,
          gridLines: {
            drawBorder: false,
            color: 'rgba(29,140,248,0.0)',
            zeroLineColor: "transparent",
          },
          ticks: {
            suggestedMin: 50,
            suggestedMax: 125,
            padding: 20,
            fontColor: "#9e9e9e"
          }
        }],

        xAxes: [{
          barPercentage: 1.6,
          gridLines: {
            drawBorder: false,
            color: 'rgba(0,242,195,0.1)',
            zeroLineColor: "transparent",
          },
          ticks: {
            padding: 20,
            fontColor: "#9e9e9e"
          }
        }]
      }
    };


    gradientBarChartConfiguration = {
      maintainAspectRatio: false,
      legend: {
        display: false
      },

      tooltips: {
        backgroundColor: '#f5f5f5',
        titleFontColor: '#333',
        bodyFontColor: '#666',
        bodySpacing: 4,
        xPadding: 12,
        mode: "nearest",
        intersect: 0,
        position: "nearest"
      },
      responsive: true,
      scales: {
        yAxes: [{

          gridLines: {
            drawBorder: false,
            color: 'rgba(29,140,248,0.1)',
            zeroLineColor: "transparent",
          },
          ticks: {
            suggestedMin: 60,
            suggestedMax: 120,
            padding: 20,
            fontColor: "#9e9e9e"
          }
        }],

        xAxes: [{

          gridLines: {
            drawBorder: false,
            color: 'rgba(29,140,248,0.1)',
            zeroLineColor: "transparent",
          },
          ticks: {
            padding: 20,
            fontColor: "#9e9e9e"
          }
        }]
      }
    };

    // var ctx = document.getElementById("chartLinePurple").getContext("2d");

    // var gradientStroke = ctx.createLinearGradient(0, 230, 0, 50);

    // gradientStroke.addColorStop(1, 'rgba(72,72,176,0.2)');
    // gradientStroke.addColorStop(0.2, 'rgba(72,72,176,0.0)');
    // gradientStroke.addColorStop(0, 'rgba(119,52,169,0)'); //purple colors

    // var data = {
    //   labels: ['JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC'],
    //   datasets: [{
    //     label: "Data",
    //     fill: true,
    //     backgroundColor: gradientStroke,
    //     borderColor: '#d048b6',
    //     borderWidth: 2,
    //     borderDash: [],
    //     borderDashOffset: 0.0,
    //     pointBackgroundColor: '#d048b6',
    //     pointBorderColor: 'rgba(255,255,255,0)',
    //     pointHoverBackgroundColor: '#d048b6',
    //     pointBorderWidth: 20,
    //     pointHoverRadius: 4,
    //     pointHoverBorderWidth: 15,
    //     pointRadius: 4,
    //     data: [80, 100, 70, 80, 120, 80],
    //   }]
    // };

    // var myChart = new Chart(ctx, {
    //   type: 'line',
    //   data: data,
    //   options: gradientChartOptionsConfigurationWithTooltipPurple
    // });
    // var ctx = document.getElementById("chartLinePurple").getContext("2d");

    // var gradientStroke = ctx.createLinearGradient(0, 230, 0, 50);

    // gradientStroke.addColorStop(1, 'rgba(72,72,176,0.2)');
    // gradientStroke.addColorStop(0.2, 'rgba(72,72,176,0.0)');
    // gradientStroke.addColorStop(0, 'rgba(119,52,169,0)'); // purple colors

    // // Generate labels for each minute (example for 10 minutes)
    // var labels = [];
    // for (let i = 0; i < 10; i++) {
    //   labels.push(`Min ${i + 1}`);
    // }

    // // Initial sample data for each minute
    // var dataValues = [80, 85, 90, 95, 100, 105, 110, 115, 120, 125];

    // var data = {
    //   labels: labels,
    //   datasets: [{
    //     label: "Stock Prices",
    //     fill: true,
    //     backgroundColor: gradientStroke,
    //     borderColor: '#d048b6',
    //     borderWidth: 2,
    //     borderDash: [],
    //     borderDashOffset: 0.0,
    //     pointBackgroundColor: '#d048b6',
    //     pointBorderColor: 'rgba(255,255,255,0)',
    //     pointHoverBackgroundColor: '#d048b6',
    //     pointBorderWidth: 20,
    //     pointHoverRadius: 4,
    //     pointHoverBorderWidth: 15,
    //     pointRadius: 4,
    //     data: dataValues,
    //   }]
    // };

    // // Create the chart using Chart.js (assuming you have included Chart.js in your project)
    // var chart = new Chart(ctx, {
    //   type: 'line',
    //   data: data,
    //   options: {
    //     responsive: true,
    //     maintainAspectRatio: false,
    //     scales: {
    //       x: {
    //         ticks: {
    //           autoSkip: false
    //         }
    //       }
    //     }
    //   }
    // });
    var currentCompanyIndex = 0;
    var companies = [];

    function fetchData() {
      fetch('/api/get_details')
        .then(response => response.json())
        .then(data => {
          companies = Object.keys(data['total_worktime']);
          updateChart(data['total_worktime']);
          updateChartLateEarly(data);
        })
        .catch(error => console.error('Error:', error));
    }

    function updateChart(data) {
      if (companies.length === 0) return;

      var company = companies[currentCompanyIndex];
      var ctx = document.getElementById("chartLinePurple").getContext("2d");

      var gradientStroke = ctx.createLinearGradient(0, 230, 0, 50);
      gradientStroke.addColorStop(1, 'rgba(72,72,176,0.2)');
      gradientStroke.addColorStop(0.2, 'rgba(72,72,176,0.0)');
      gradientStroke.addColorStop(0, 'rgba(119,52,169,0)'); // purple colors

      var labels = Array.from({ length: 31 }, (_, i) => `Day ${i + 1}`);
      var dataValues = data[company] || [];

      var chartData = {
        labels: labels,
        datasets: [{
          label: company,
          fill: true,
          backgroundColor: gradientStroke,
          borderColor: '#d048b6',
          borderWidth: 2,
          borderDash: [],
          borderDashOffset: 0.0,
          pointBackgroundColor: '#d048b6',
          pointBorderColor: 'rgba(255,255,255,0)',
          pointHoverBackgroundColor: '#d048b6',
          pointBorderWidth: 20,
          pointHoverRadius: 4,
          pointHoverBorderWidth: 15,
          pointRadius: 4,
          data: dataValues,
        }]
      };

      var myChart = new Chart(ctx, {
        type: 'line',
        data: chartData,
        options: {
          responsive: true,
          legend: {
            display: true,
          },
          scales: {
            xAxes: [{
              ticks: {
                autoSkip: true,
                maxTicksLimit: 31
              }
            }],
            yAxes: [{
              ticks: {
                beginAtZero: true
              }
            }]
          }
        }
      });
    
      // Cập nhật thẻ h5 với tên công ty hiện tại
      document.getElementById('worktime_company').innerText = `Total work time for ${company}`;
    
      currentCompanyIndex = (currentCompanyIndex + 1) % companies.length;
    }

    // Gọi hàm fetchData ban đầu
    fetchData();

    // Thiết lập interval để cập nhật biểu đồ mỗi 20 giây
    setInterval(() => {
      fetch('/api/get_details')
        .then(response => response.json())
        .then(data => {
          updateChart(data['total_worktime']);
          updateChartLateEarly(data);
        })
        .catch(error => console.error('Error:', error));
    }, 20000);    
    // Function to fetch sample stock prices (replacing this with real API call in real scenarios)
    function fetchStockPrices() {
      // Sample JSON string with new data
      const sampleJson = `{
        "prices": [90, 95, 100, 105, 110, 115, 120, 125, 130, 135]
      }`;

      const data = JSON.parse(sampleJson);
      return data.prices;
    }

    // Function to update chart data
    function updateChartData() {
      const prices = fetchStockPrices();

      // Update chart data
      chart.data.datasets[0].data = prices;
      chart.update();
    }

    // Update chart data periodically (e.g., every 5 seconds)
    setInterval(updateChartData, 5000); // Update every 5 seconds

    var ctx = document.getElementById("chartLineGreen").getContext("2d");

    var gradientStrokeBlue = ctx.createLinearGradient(0, 230, 0, 50);
    gradientStrokeBlue.addColorStop(1, 'rgba(66, 134, 244, 0.2)');
    gradientStrokeBlue.addColorStop(0.2, 'rgba(66, 134, 244, 0.0)');
    gradientStrokeBlue.addColorStop(0, 'rgba(66, 134, 244, 0)'); // blue colors

    var gradientStrokeRed = ctx.createLinearGradient(0, 230, 0, 50);
    gradientStrokeRed.addColorStop(1, 'rgba(244, 66, 66, 0.2)');
    gradientStrokeRed.addColorStop(0.2, 'rgba(244, 66, 66, 0.0)');
    gradientStrokeRed.addColorStop(0, 'rgba(244, 66, 66, 0)'); // red colors

    // Example data
    var labels = Array.from({ length: 31 }, (_, i) => `Day ${i + 1}`);
    var startTimes = [8, 8.5, 9, 8, 8, 9, 8, 8.5, 9, 8, 8, 9, 8, 8.5, 9, 8, 8, 9, 8, 8.5, 9, 8, 8, 9, 8, 8.5, 9, 8, 8, 9, 8];
    var endTimes = [17, 17.5, 18, 17, 17, 18, 17, 17.5, 18, 17, 17, 18, 17, 17.5, 18, 17, 17, 18, 17, 17.5, 18, 17, 17, 18, 17, 17.5, 18, 17, 17, 18, 17];

    var data = {
      labels: labels,
      datasets: [
        {
          label: "Start Time",
          fill: true,
          backgroundColor: gradientStrokeBlue,
          borderColor: '#4286f4',
          borderWidth: 2,
          pointBackgroundColor: '#4286f4',
          pointBorderColor: 'rgba(255,255,255,0)',
          pointHoverBackgroundColor: '#4286f4',
          pointBorderWidth: 20,
          pointHoverRadius: 4,
          pointHoverBorderWidth: 15,
          pointRadius: 4,
          data: startTimes,
        },
        {
          label: "End Time",
          fill: true,
          backgroundColor: gradientStrokeRed,
          borderColor: '#f44242',
          borderWidth: 2,
          pointBackgroundColor: '#f44242',
          pointBorderColor: 'rgba(255,255,255,0)',
          pointHoverBackgroundColor: '#f44242',
          pointBorderWidth: 20,
          pointHoverRadius: 4,
          pointHoverBorderWidth: 15,
          pointRadius: 4,
          data: endTimes,
        }
      ]
    };

    // Create the chart using Chart.js
    var chart = new Chart(ctx, {
      type: 'line',
      data: data,
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: {
            title: {
              display: true,
              text: 'Day of the Month'
            }
          },
          y: {
            title: {
              display: true,
              text: 'Time (Hours)'
            },
            ticks: {
              beginAtZero: true,
              max: 24
            }
          }
        }
      }
    });

    // Function to fetch sample work times (replace this with real API call in real scenarios)
    function fetchWorkTimes() {
      // Sample JSON string with new data
      const sampleJson = `{
    "startTimes": [8, 8.5, 9, 8, 8, 9, 8, 8.5, 9, 8, 8, 9, 8, 8.5, 9, 8, 8, 9, 8, 8.5, 9, 8, 8, 9, 8, 8.5, 9, 8, 8, 9, 8],
    "endTimes": [17, 17.5, 18, 17, 17, 18, 17, 17.5, 18, 17, 17, 18, 17, 17.5, 18, 17, 17, 18, 17, 17.5, 18, 17, 17, 18, 17, 17.5, 18, 17, 17, 18, 17]
  }`;

      const data = JSON.parse(sampleJson);
      return data;
    }

    // Function to update chart data
    function updateChartData() {
      const workTimes = fetchWorkTimes();

      // Update chart data
      chart.data.datasets[0].data = workTimes.startTimes;
      chart.data.datasets[1].data = workTimes.endTimes;
      chart.update();
    }

    // Update chart data periodically (e.g., every hour)
    setInterval(updateChartData, 3600000); // Update every 1 hour


    // var ctxGreen = document.getElementById("chartLineGreen").getContext("2d");

    // var gradientStroke = ctx.createLinearGradient(0, 230, 0, 50);

    // gradientStroke.addColorStop(1, 'rgba(66,134,121,0.15)');
    // gradientStroke.addColorStop(0.4, 'rgba(66,134,121,0.0)'); //green colors
    // gradientStroke.addColorStop(0, 'rgba(66,134,121,0)'); //green colors

    // var data = {
    //   labels: ['JUL', 'AUG', 'SEP', 'OCT', 'NOV'],
    //   datasets: [{
    //     label: "My First dataset",
    //     fill: true,
    //     backgroundColor: gradientStroke,
    //     borderColor: '#00d6b4',
    //     borderWidth: 2,
    //     borderDash: [],
    //     borderDashOffset: 0.0,
    //     pointBackgroundColor: '#00d6b4',
    //     pointBorderColor: 'rgba(255,255,255,0)',
    //     pointHoverBackgroundColor: '#00d6b4',
    //     pointBorderWidth: 20,
    //     pointHoverRadius: 4,
    //     pointHoverBorderWidth: 15,
    //     pointRadius: 4,
    //     data: [90, 27, 60, 12, 80],
    //   }]
    // };

    // var myChart = new Chart(ctxGreen, {
    //   type: 'line',
    //   data: data,
    //   options: gradientChartOptionsConfigurationWithTooltipGreen

    // });
    var canvas = document.getElementById('projectgantt');
    var ctx = canvas.getContext('2d');

    // Tạo gradient cho các task
    var gradientStroke = ctx.createLinearGradient(0, 230, 0, 50);
    gradientStroke.addColorStop(1, 'rgba(72,72,176,0.1)');
    gradientStroke.addColorStop(0.4, 'rgba(72,72,176,0.0)');
    gradientStroke.addColorStop(0, 'rgba(119,52,169,0)');

    var tasks = [
      { name: "Task 1", start: 0, end: 3 },
      { name: "Task 2", start: 2, end: 7 },
      { name: "Task 3", start: 5, end: 10 }
    ];

    var taskHeight = 30;
    var taskGap = 10;
    var xOffset = 100;

    ctx.font = '16px Arial';
    ctx.textBaseline = 'middle';

    tasks.forEach(function(task, index) {
      var y = index * (taskHeight + taskGap);
      var startX = xOffset + task.start * 50;
      var endX = xOffset + task.end * 50;

      ctx.fillStyle = gradientStroke;
      ctx.fillRect(startX, y, endX - startX, taskHeight);

      ctx.fillStyle = '#000';
      ctx.fillText(task.name, 10, y + taskHeight / 2);
    });

    // Vẽ trục thời gian
    ctx.beginPath();
    ctx.moveTo(xOffset, 0);
    ctx.lineTo(xOffset, canvas.height);
    ctx.stroke();

    for (var i = 0; i <= 10; i++) {
      ctx.beginPath();
      ctx.moveTo(xOffset + i * 50, 0);
      ctx.lineTo(xOffset + i * 50, canvas.height);
      ctx.strokeStyle = '#d3d3d3';
      ctx.stroke();

      ctx.fillStyle = '#000';
      ctx.fillText(i, xOffset + i * 50 - 5, canvas.height - 10);
    }

    var canvas = document.getElementById('projectgantt2');
    var ctx = canvas.getContext('2d');

    // Tạo gradient cho các task
    var gradientStroke = ctx.createLinearGradient(0, 230, 0, 50);
    gradientStroke.addColorStop(1, 'rgba(72,72,176,0.1)');
    gradientStroke.addColorStop(0.4, 'rgba(72,72,176,0.0)');
    gradientStroke.addColorStop(0, 'rgba(119,52,169,0)');

    var tasks = [
      { name: "Task 1", start: 0, end: 3 },
      { name: "Task 2", start: 2, end: 7 },
      { name: "Task 3", start: 5, end: 10 }
    ];

    var taskHeight = 30;
    var taskGap = 10;
    var xOffset = 100;

    ctx.font = '16px Arial';
    ctx.textBaseline = 'middle';

    tasks.forEach(function(task, index) {
      var y = index * (taskHeight + taskGap);
      var startX = xOffset + task.start * 50;
      var endX = xOffset + task.end * 50;

      ctx.fillStyle = gradientStroke;
      ctx.fillRect(startX, y, endX - startX, taskHeight);

      ctx.fillStyle = '#000';
      ctx.fillText(task.name, 10, y + taskHeight / 2);
    });

    // Vẽ trục thời gian
    ctx.beginPath();
    ctx.moveTo(xOffset, 0);
    ctx.lineTo(xOffset, canvas.height);
    ctx.stroke();

    for (var i = 0; i <= 10; i++) {
      ctx.beginPath();
      ctx.moveTo(xOffset + i * 50, 0);
      ctx.lineTo(xOffset + i * 50, canvas.height);
      ctx.strokeStyle = '#d3d3d3';
      ctx.stroke();

      ctx.fillStyle = '#000';
      ctx.fillText(i, xOffset + i * 50 - 5, canvas.height - 10);
    }

    var chart_labels = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC'];
    var chart_data = [100, 70, 90, 70, 85, 60, 75, 60, 90, 80, 110, 100];


    var ctx = document.getElementById("chartBig1").getContext('2d');

    var gradientStroke = ctx.createLinearGradient(0, 230, 0, 50);

    gradientStroke.addColorStop(1, 'rgba(72,72,176,0.1)');
    gradientStroke.addColorStop(0.4, 'rgba(72,72,176,0.0)');
    gradientStroke.addColorStop(0, 'rgba(119,52,169,0)'); //purple colors
    var config = {
      type: 'line',
      data: {
        labels: chart_labels,
        datasets: [{
          label: "My First dataset",
          fill: true,
          backgroundColor: gradientStroke,
          borderColor: '#d346b1',
          borderWidth: 2,
          borderDash: [],
          borderDashOffset: 0.0,
          pointBackgroundColor: '#d346b1',
          pointBorderColor: 'rgba(255,255,255,0)',
          pointHoverBackgroundColor: '#d346b1',
          pointBorderWidth: 20,
          pointHoverRadius: 4,
          pointHoverBorderWidth: 15,
          pointRadius: 4,
          data: chart_data,
        }]
      },
      options: gradientChartOptionsConfigurationWithTooltipPurple
    };
    var myChartData = new Chart(ctx, config);
    $("#0").click(function() {
      var data = myChartData.config.data;
      data.datasets[0].data = chart_data;
      data.labels = chart_labels;
      myChartData.update();
    });
    $("#1").click(function() {
      var chart_data = [80, 120, 105, 110, 95, 105, 90, 100, 80, 95, 70, 120];
      var data = myChartData.config.data;
      data.datasets[0].data = chart_data;
      data.labels = chart_labels;
      myChartData.update();
    });

    $("#2").click(function() {
      var chart_data = [60, 80, 65, 130, 80, 105, 90, 130, 70, 115, 60, 130];
      var data = myChartData.config.data;
      data.datasets[0].data = chart_data;
      data.labels = chart_labels;
      myChartData.update();
    });


    // var ctx = document.getElementById("CountryChartDaily").getContext("2d");

    // var gradientStroke = ctx.createLinearGradient(0, 230, 0, 50);

    // gradientStroke.addColorStop(1, 'rgba(29,140,248,0.2)');
    // gradientStroke.addColorStop(0.4, 'rgba(29,140,248,0.0)');
    // gradientStroke.addColorStop(0, 'rgba(29,140,248,0)'); //blue colors


    // var myChart = new Chart(ctx, {
    //   type: 'bar',
    //   responsive: true,
    //   legend: {
    //     display: false
    //   },
    //   data: {
    //     labels: ['USA', 'GER', 'AUS', 'UK', 'RO', 'BR'],
    //     datasets: [{
    //       label: "Countries",
    //       fill: true,
    //       backgroundColor: gradientStroke,
    //       hoverBackgroundColor: gradientStroke,
    //       borderColor: '#1f8ef1',
    //       borderWidth: 2,
    //       borderDash: [],
    //       borderDashOffset: 0.0,
    //       data: [53, 20, 10, 80, 100, 45],
    //     }]
    //   },
    //   options: gradientBarChartConfiguration
    // });
    var ctx = document.getElementById("CountryChartDaily").getContext("2d");

    var gradientStrokeBlue = ctx.createLinearGradient(0, 230, 0, 50);
    gradientStrokeBlue.addColorStop(1, 'rgba(29,140,248,0.2)');
    gradientStrokeBlue.addColorStop(0.4, 'rgba(29,140,248,0.0)');
    gradientStrokeBlue.addColorStop(0, 'rgba(29,140,248,0)'); // blue

    var gradientStrokeRed = ctx.createLinearGradient(0, 230, 0, 50);
    gradientStrokeRed.addColorStop(1, 'rgba(248,29,29,0.2)');
    gradientStrokeRed.addColorStop(0.4, 'rgba(248,29,29,0.0)');
    gradientStrokeRed.addColorStop(0, 'rgba(248,29,29,0)'); // red

    var myChart = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: ['USA', 'GER', 'AUS', 'UK', 'RO', 'BR'],
        datasets: [{
          label: "Blue",
          backgroundColor: gradientStrokeBlue,
          borderColor: '#1f8ef1',
          borderWidth: 2,
          data: [53, 20, 10, 80, 100, 45],
        }, {
          label: "Red",
          backgroundColor: gradientStrokeRed,
          borderColor: '#f81d1d',
          borderWidth: 2,
          data: [30, 40, 25, 60, 90, 35],
        }]
      },
      options: {
        responsive: true,
        legend: {
          display: true,
        },
        scales: {
          xAxes: [{
            barPercentage: 0.8,
            categoryPercentage: 0.4,
          }],
          yAxes: [{
            ticks: {
              beginAtZero: true
            }
          }]
        }
      }
    });
//     var currentCompanyIndex = 0;
// var companies = [];

    // function fetchDataLateEarly() {
    //   fetch('/api/get_details')
    //     .then(response => response.json())
    //     .then(data => {
    //       companies = Object.keys(data['total_worktime']);
    //       updateChartLateEarly(data);
    //     })
    //     .catch(error => console.error('Error:', error));
    // }

    function updateChartLateEarly(data) {
      if (companies.length === 0) return;

      var company = companies[currentCompanyIndex];
      currentCompanyIndex = (currentCompanyIndex + 1) % companies.length;

      var ctx = document.getElementById("CountryChart").getContext("2d");

      var gradientStrokeBlue = ctx.createLinearGradient(0, 230, 0, 50);
      gradientStrokeBlue.addColorStop(1, 'rgba(29,140,248,0.2)');
      gradientStrokeBlue.addColorStop(0.4, 'rgba(29,140,248,0.0)');
      gradientStrokeBlue.addColorStop(0, 'rgba(29,140,248,0)'); // blue

      var gradientStrokeRed = ctx.createLinearGradient(0, 230, 0, 50);
      gradientStrokeRed.addColorStop(1, 'rgba(248,29,29,0.2)');
      gradientStrokeRed.addColorStop(0.4, 'rgba(248,29,29,0.0)');
      gradientStrokeRed.addColorStop(0, 'rgba(248,29,29,0)'); // red

      // Get the number of days in the current month
      var date = new Date();
      var year = date.getFullYear();
      var month = date.getMonth() + 1; // JavaScript months are 0-11
      var daysInMonth = new Date(year, month, 0).getDate();

      // Generate labels based on the number of days
      var labels = Array.from({ length: daysInMonth }, (_, i) => `Day ${i + 1}`);

      var chartData = {
        labels: labels,
        datasets: [{
          label: "In Time",
          backgroundColor: gradientStrokeBlue,
          borderColor: '#1f8ef1',
          borderWidth: 2,
          data: data.in_time[company],
        }, {
          label: "Late/Early",
          backgroundColor: gradientStrokeRed,
          borderColor: '#f81d1d',
          borderWidth: 2,
          data: data.late_early[company],
        }]
      };

      var myChart = new Chart(ctx, {
        type: 'bar',
        data: chartData,
        options: {
          responsive: true,
          legend: {
            display: true,
          },
          scales: {
            xAxes: [{
              barPercentage: 0.8,
              categoryPercentage: 0.4,
            }],
            yAxes: [{
              ticks: {
                beginAtZero: true
              }
            }]
          }
        }
      });
    }

    // Fetch data and update chart every 20 seconds
    // fetchDataLateEarly();
    // setInterval(fetchDataLateEarly, 20000); // 20 seconds interval


  },

  initGoogleMaps: function() {
    var myLatlng = new google.maps.LatLng(40.748817, -73.985428);
    var mapOptions = {
      zoom: 13,
      center: myLatlng,
      scrollwheel: false, //we disable de scroll over the map, it is a really annoing when you scroll through page
      styles: [{
          "elementType": "geometry",
          "stylers": [{
            "color": "#1d2c4d"
          }]
        },
        {
          "elementType": "labels.text.fill",
          "stylers": [{
            "color": "#8ec3b9"
          }]
        },
        {
          "elementType": "labels.text.stroke",
          "stylers": [{
            "color": "#1a3646"
          }]
        },
        {
          "featureType": "administrative.country",
          "elementType": "geometry.stroke",
          "stylers": [{
            "color": "#4b6878"
          }]
        },
        {
          "featureType": "administrative.land_parcel",
          "elementType": "labels.text.fill",
          "stylers": [{
            "color": "#64779e"
          }]
        },
        {
          "featureType": "administrative.province",
          "elementType": "geometry.stroke",
          "stylers": [{
            "color": "#4b6878"
          }]
        },
        {
          "featureType": "landscape.man_made",
          "elementType": "geometry.stroke",
          "stylers": [{
            "color": "#334e87"
          }]
        },
        {
          "featureType": "landscape.natural",
          "elementType": "geometry",
          "stylers": [{
            "color": "#023e58"
          }]
        },
        {
          "featureType": "poi",
          "elementType": "geometry",
          "stylers": [{
            "color": "#283d6a"
          }]
        },
        {
          "featureType": "poi",
          "elementType": "labels.text.fill",
          "stylers": [{
            "color": "#6f9ba5"
          }]
        },
        {
          "featureType": "poi",
          "elementType": "labels.text.stroke",
          "stylers": [{
            "color": "#1d2c4d"
          }]
        },
        {
          "featureType": "poi.park",
          "elementType": "geometry.fill",
          "stylers": [{
            "color": "#023e58"
          }]
        },
        {
          "featureType": "poi.park",
          "elementType": "labels.text.fill",
          "stylers": [{
            "color": "#3C7680"
          }]
        },
        {
          "featureType": "road",
          "elementType": "geometry",
          "stylers": [{
            "color": "#304a7d"
          }]
        },
        {
          "featureType": "road",
          "elementType": "labels.text.fill",
          "stylers": [{
            "color": "#98a5be"
          }]
        },
        {
          "featureType": "road",
          "elementType": "labels.text.stroke",
          "stylers": [{
            "color": "#1d2c4d"
          }]
        },
        {
          "featureType": "road.highway",
          "elementType": "geometry",
          "stylers": [{
            "color": "#2c6675"
          }]
        },
        {
          "featureType": "road.highway",
          "elementType": "geometry.fill",
          "stylers": [{
            "color": "#9d2a80"
          }]
        },
        {
          "featureType": "road.highway",
          "elementType": "geometry.stroke",
          "stylers": [{
            "color": "#9d2a80"
          }]
        },
        {
          "featureType": "road.highway",
          "elementType": "labels.text.fill",
          "stylers": [{
            "color": "#b0d5ce"
          }]
        },
        {
          "featureType": "road.highway",
          "elementType": "labels.text.stroke",
          "stylers": [{
            "color": "#023e58"
          }]
        },
        {
          "featureType": "transit",
          "elementType": "labels.text.fill",
          "stylers": [{
            "color": "#98a5be"
          }]
        },
        {
          "featureType": "transit",
          "elementType": "labels.text.stroke",
          "stylers": [{
            "color": "#1d2c4d"
          }]
        },
        {
          "featureType": "transit.line",
          "elementType": "geometry.fill",
          "stylers": [{
            "color": "#283d6a"
          }]
        },
        {
          "featureType": "transit.station",
          "elementType": "geometry",
          "stylers": [{
            "color": "#3a4762"
          }]
        },
        {
          "featureType": "water",
          "elementType": "geometry",
          "stylers": [{
            "color": "#0e1626"
          }]
        },
        {
          "featureType": "water",
          "elementType": "labels.text.fill",
          "stylers": [{
            "color": "#4e6d70"
          }]
        }
      ]
    };

    var map = new google.maps.Map(document.getElementById("map"), mapOptions);

    var marker = new google.maps.Marker({
      position: myLatlng,
      title: "Hello World!"
    });

    // To add the marker to the map, call setMap();
    marker.setMap(map);
  },

  showNotification: function(from, align) {
    color = Math.floor((Math.random() * 4) + 1);

    $.notify({
      icon: "tim-icons icon-bell-55",
      message: "Welcome to <b>Black Dashboard</b> - a beautiful freebie for every web developer."

    }, {
      type: type[color],
      timer: 8000,
      placement: {
        from: from,
        align: align
      }
    });
  }

};