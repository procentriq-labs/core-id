(function () {
    const hiddenDataElement = document.querySelector("#hidden-data");
    if (hiddenDataElement && hiddenDataElement.getAttribute("data-email-sent") === "True") {
        const url = new URL(window.location.href);
        url.searchParams.set('mail_sent', '1');
        window.history.replaceState({}, document.title, url.toString());
    }
})();