(function () {
    function launchForSafari(event) {
        var $button = $(event.currentTarget);
        var canvasToolUrl = $button.attr('data-referer');
        var popup = window.open('/safari', 'toolbar=no,status=no,width=100,height=100');
        $(popup).on('load', function () {
            popup.close();
            window.parent.location.href = canvasToolUrl;
        });
    }

    $(document).ready(function () {
        $('#launch-button').click(launchForSafari);
    });
})();