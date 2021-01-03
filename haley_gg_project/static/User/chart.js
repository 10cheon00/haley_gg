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
                    backgroundColor: ['#FF8A57'],
                    hoverBackgroundColor: ['#FFB291'],
                },
            ],
        },
        options: {
            plugins: {
                datalabels: {
                    display: true,
                    align: 'center',
                    anchor: 'center'
                }
            },
            pieceLabel: {
                mode:"value",
                position:"outside",
                fontSize: 11,
                fontStyle: 'bold' 
            },
            responsive: true,
        },
    });
}