function readit(id, self) {
    if (self.hasClass('read-it')) {
        self.removeClass('read-it')
        self.addClass('not-read')
        $.post('/readit/' + id, function(data) {
            if (!data.success) {
                self.addClass('read-it')
            }
        })
    }
    else {
        self.removeClass('not-read')
        self.addClass('read-it')
        $.post('/readit/' + id, function(data) {
            if (!data.success) {
                self.removeClass('read-it')
            }
        })
    } 
}

function saveit(id, self) {
    if (self.hasClass('saved')) {
        self.removeClass('saved')
        $.post('/saveit/' + id, function(data) {
            if (!data.success) {
                self.addClass('saved')
            }
        })
    }
    else {
        self.addClass('saved')
        $.post('/saveit/' + id, function(data) {
            if (!data.success) {
                self.removeClass('saved')
            }
        })
    } 
}

function loveit(id, self) {
    if (self.hasClass('loved')) {
        self.removeClass('loved')
        $.post('/loveit/' + id, function(data) {
            if (!data.success) {
                self.addClass('loved')
            }
        })
    }
    else {
        self.addClass('loved')
        $.post('/loveit/' + id, function(data) {
            if (!data.success) {
                self.removeClass('loved')
            }
        })
    } 
}

$('form').submit(function() {
    if ($('#form-unread').prop('checked')) {
        $('#form-unread-hidden').prop('disabled', true);
    }
    if ($('#form-ignore').prop('checked')) {
        $('#form-ignore-hidden').prop('disabled', true);
    }
})

function openAll() {
    var links = $(".reddit-link").toArray();
    links.forEach(link => window.open(link.href, "_blank"));
}

$("#feed-form").submit((e) => {
    feedMore();
    e.preventDefault();
})

function readAll() {
    var ids = [];
    $('.post').each((idx, value) => {
        ids.push(value.id);
    })

    $.post("/readall", {
        posts: ids
    }).done((data) => {
        if (!data.success) {
            console.log('failed');
            return;
        }
    }).done(() => {
        feedMore();
    })
}

function feedMore() {
    // var btns = $(".not-read").each((idx, btn) => btn.click());
    $.post("/feedmore", {
            subreddit: $("#form-subreddit").prop('value'),
            max_age: $("#form-age").prop('value')
        },
    ).done((data) => {
        $("#feed").empty();
        document.getElementById('feed').innerHTML = data.html;
})
}