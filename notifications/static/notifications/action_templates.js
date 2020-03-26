// Stolen from django-import-export :)
(function($) {
    $(document).ready(function() {
        var $actionsSelect, $formatsElement;
        if ($('body').hasClass('grp-change-list')) {
            // using grappelli
            $actionsSelect = $('#grp-changelist-form select[name="action"]');
            $formatsElement = $('#grp-changelist-form select[name="template"]');
        } else {
            // using default admin
            $actionsSelect = $('#changelist-form select[name="action"]');
            $formatsElement = $('#changelist-form select[name="template"]').parent();
        }
        $actionsSelect.change(function() {
            if ($(this).val() === 'notify_action') {
                $formatsElement.show();
            } else {
                $formatsElement.hide();
            }
        });
        $actionsSelect.change();
    });
})(django.jQuery);
