function readit(id, self) {
    if (self.hasClass('read-it')) {
        self.removeClass('read-it')
        $.post('/readit/' + id, function(data) {
            if (!data.success) {
                self.addClass('read-it')
            }
        })
    }
    else {
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