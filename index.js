document.addEventListener('DOMContentLoaded', function() {
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

    let form = document.getElementById('form');
    form.addEventListener('submit', function(event) {
        event.preventDefault();
        console.log(form)
        let send = new FormData(this);
        fetch('http://127.0.0.1:5379/search', {
            method: 'POST',
            body: send
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