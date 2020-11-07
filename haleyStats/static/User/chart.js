function new_chart(name, race, rates){
    var ctxP = document.getElementById(name).getContext('2d');
    console.log(ctxP)
    var myPieChart = new Chart(ctxP, {
        type: 'pie',
        data: {
            labels: [race],
            datasets: [
                {
                    data: [rates],
                    backgroundColor: ['#DDDDDD'],
                    hoverBackgroundColor: ['#999999'],
                },
            ],
        },
        options: {
            responsive: true,
        },
    });
}