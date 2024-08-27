document.addEventListener('DOMContentLoaded', function() {
    let form = document.getElementById('form');
    let subject = document.getElementById('subject');
    fetch('http://127.0.0.1:5379/subjects').then(response => response.json())
    .then(data => {
        console.log(data)
        data.subjects.forEach(element => {
            let option = document.createElement('option');
            option.value = element.code;
            option.text = element.name;
            subject.add(option);
    })


    form.addEventListener('submit', function(event) {
        event.preventDefault();
        let send = {
            code: document.getElementById('code').value,
            qp: document.querySelector('input[name="variant"]:checked').value
        }
        console.log(send)
        fetch('http://127.0.0.1:5379/search', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(send)
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                document.getElementById('result').src = ''
                alert(data.error)
                return
            }
            document.getElementById('result').src = data.link
        })
        
    });
});});