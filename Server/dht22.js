document.addEventListener("DOMContentLoaded", function () {
    fetch('sensores_data.json')
        .then(response => response.json())
        .then(data => {
            const dataDisplay = document.getElementById("DHT22");

            const table = document.createElement("table");
            const thead = document.createElement("thead");
            const tbody = document.createElement("tbody");

            const headerRow = document.createElement("tr");
            const headers = ["Id", "Sensor", "Temperatura", "Humedad", "Hora"];
            headers.forEach(headerText => {
                const th = document.createElement("th");
                th.textContent = headerText;
                headerRow.appendChild(th);
            });
            thead.appendChild(headerRow);

            data.forEach(sensorData => {
                const row = document.createElement("tr");

                const idCell = document.createElement("td");
                idCell.textContent = sensorData.id;
                row.appendChild(idCell);

                const sensorCell = document.createElement("td");
                sensorCell.textContent = sensorData.sensor;
                row.appendChild(sensorCell);

                const temperaturaCell = document.createElement("td");
                temperaturaCell.textContent = sensorData.temperatura;
                row.appendChild(temperaturaCell);

                const humedadCell = document.createElement("td");
                humedadCell.textContent = sensorData.humedad;
                row.appendChild(humedadCell);

                const timeCell = document.createElement("td");
                const date = new Date(sensorData.timestamp);
                timeCell.textContent = date.toLocaleString();
                row.appendChild(timeCell);

                tbody.appendChild(row);
            });

            table.appendChild(thead);
            table.appendChild(tbody);

            dataDisplay.appendChild(table);
        })
        .catch(error => console.error("Error fetching JSON data:", error));
});
