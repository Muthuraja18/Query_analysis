function ask() {
    let q = document.getElementById("query").value;

    fetch("/ask", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({query: q})
    })
    .then(res => res.json())
    .then(data => {
        document.getElementById("output").innerHTML = `
            <h3>🤖 Groq:</h3>
            <p>${data.groq}</p>

            <h3>📦 Product Info:</h3>
            <p><b>${data.product.product}</b></p>
            <p>Price: ${data.product.price}</p>
            <p>Discount: ${data.product.discount}%</p>

            <h3>😊 Sentiment:</h3>
            <p>${data.sentiment} ${data.emoji}</p>
        `;
    });
}
