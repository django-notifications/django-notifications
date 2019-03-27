console.log('running tester')

function make_notification() {
    var r = new XMLHttpRequest();
    r.open("GET", '/test_make/', true);
    r.send();
}