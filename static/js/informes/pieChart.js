const randomColorGenerator = function () {
    return '#' + (Math.random().toString(16) + '0000000').slice(2, 8);
};

function newPieChart(ctx, data) {
    const labels = [];
    const values = [];
    const colors = [];
    data.forEach((item) => {
        labels.push(item.name);
        values.push(item.value);
        colors.push(randomColorGenerator())
    });
    const config = {
        type: 'pie',
        data: {
            datasets: [{
                data: values,
                backgroundColor: colors,
                label: 'Grafica'
            }],
            labels: labels
        },
        options: {
            responsive: true
        }
    };
    new Chart(ctx, config);
}