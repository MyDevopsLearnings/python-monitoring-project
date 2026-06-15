const labels = [];

const cpuData = [];
const memoryData = [];
const diskData = [];

function createChart(id, label) {

    return new Chart(
        document.getElementById(id),
        {
            type: 'line',

            data: {
                labels: labels,
                datasets: [{
                    label: label,
                    data: [],
                    tension: 0.3
                }]
            },

            options: {
                responsive: true,
                animation: false
            }
        }
    );
}

const cpuChart = createChart(
    "cpuChart",
    "CPU Usage %"
);

const memoryChart = createChart(
    "memoryChart",
    "Memory Usage %"
);

const diskChart = createChart(
    "diskChart",
    "Disk Usage %"
);

async function loadDashboard() {

    try {

        const resource =
            await fetch("/resource-usage");

        const resourceData =
            await resource.json();

        const health =
            await fetch("/health");

        const healthData =
            await health.json();

        const uptime =
            await fetch("/uptime");

        const uptimeData =
            await uptime.json();

        const requests =
            await fetch("/request-count");

        const requestData =
            await requests.json();

        const processes =
            await fetch("/process-info");

        const processData =
            await processes.json();

        document.getElementById("cpu")
            .innerText =
            resourceData.cpu_percent + "%";

        document.getElementById("memory")
            .innerText =
            resourceData.memory_percent + "%";

        document.getElementById("disk")
            .innerText =
            resourceData.disk_percent + "%";

        document.getElementById("uptime")
            .innerText =
            uptimeData.uptime_minutes + " mins";

        document.getElementById("requests")
            .innerText =
            requestData.total_requests;

        const statusElement =
            document.getElementById("status");

        statusElement.innerText =
            healthData.status;

        if (healthData.status === "UP") {
            statusElement.className =
                "status-up";
        } else {
            statusElement.className =
                "status-warning";
        }

        const currentTime =
            new Date().toLocaleTimeString();

        labels.push(currentTime);

        cpuData.push(resourceData.cpu_percent);
        memoryData.push(resourceData.memory_percent);
        diskData.push(resourceData.disk_percent);

        if (labels.length > 20) {

            labels.shift();

            cpuData.shift();
            memoryData.shift();
            diskData.shift();
        }

        cpuChart.data.labels = labels;
        cpuChart.data.datasets[0].data = cpuData;
        cpuChart.update();

        memoryChart.data.labels = labels;
        memoryChart.data.datasets[0].data = memoryData;
        memoryChart.update();

        diskChart.data.labels = labels;
        diskChart.data.datasets[0].data = diskData;
        diskChart.update();

        const processTable =
            document.getElementById("processTable");

        processTable.innerHTML = "";

        processData.forEach(proc => {

            processTable.innerHTML += `
                <tr>
                    <td>${proc.pid}</td>
                    <td>${proc.name}</td>
                    <td>${proc.cpu_percent}</td>
                </tr>
            `;
        });

    }
    catch(error) {

        console.error(
            "Dashboard Load Error:",
            error
        );
    }
}

loadDashboard();

setInterval(
    loadDashboard,
    5000
);
