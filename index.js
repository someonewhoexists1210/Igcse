document.addEventListener('DOMContentLoaded', function() {
    let form = document.getElementById('form');
    form.addEventListener('submit', function(event) {
        event.preventDefault();
        let send = {
            code: document.getElementById('code').value,
        }
        console.log(send)
        fetch('/search', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(send)
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                document.getElementById('result').innerHTML = data.error
                return
            }
            document.getElementById('result').innerHTML = data.link
            document.getElementById('result').href = data.link
        })
        
    });
});