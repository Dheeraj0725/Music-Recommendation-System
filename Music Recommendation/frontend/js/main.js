const BASEURL = 'http://127.0.0.1:8000'
// function used to generate uuid
function uuidv4() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
        var r = Math.random() * 16 | 0,
            v = c == 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
    });
}

$(document).ready(function () {

    $('#search-input').prop('disabled', true);
    // generate a new UUID
    var uuid = localStorage.getItem('uuid');
    console.log(uuid)

    if (!uuid) {
        console.log("generating new");
        uuid = uuidv4();
        localStorage.setItem('uuid', uuid);
        // make API call to set token
        const apiUrl = BASEURL + '/token';
        const requestBody = { uuid: uuid };
        $.ajax({
            type: 'POST',
            url: apiUrl,
            data: JSON.stringify(requestBody),
            contentType: 'application/json',
            dataType: 'json'
        })
            .done(function (data) {
                // localStorage.setItem('token', data.token);
                $('#search-input').prop('disabled', false);
            })
            .fail(function (error) {
                console.error(error);
            });
    }else{
        $('#search-input').prop('disabled', false);
    }

    // Function to handle API search request
    function searchSpotify(query) {
        // API endpoint and search parameters
        var endpoint = BASEURL + '/search';
        var params = {
            track: query
        };

        // API request with access token header
        $.ajax({
            type: 'GET',
            url: endpoint,
            data: params,
            success: function (response) {
                // Display search suggestions in dropdown list
                var suggestions = response.items;
                var suggestionList = $("#search-suggestions");
                suggestionList.empty();
                $.each(suggestions, function (i, suggestion) {
                    var suggestionItem = $("<li>").addClass("search-suggestion").text(suggestion.name);
                    suggestionItem.attr('sid', suggestion.id);
                    suggestionItem.click(function () {
                        var sid = $(this).attr("sid");
                        $.ajax({
                            type: 'GET',
                            url: BASEURL + '/recommend?song_uri=' + sid,
                            success: function (response) {
                                $("#main-content").empty();
                                // Create a new div element and append it to the main content area
                                var resultsDiv = $("<div>").addClass("search-results");
                                var resultList = $("<ul>").addClass("search-results-list");
                                $.each(response.items, function (i, item) {
                                    var resultItem = $("<li>").addClass("search-result").text(item.name);
                                    resultList.append(resultItem);
                                });
                                resultsDiv.append(resultList);
                                $("#main-content").append(resultsDiv);
                            },
                            error: function (error) {
                                // Handle error response
                            }
                        });
                    });
                    suggestionList.append(suggestionItem);
                });
                suggestionList.show();
            }
        });
    }

    // Event handler for search input keyup
    $("#search-input").keyup(function () {
        var query = $(this).val();
        if (query.length >= 3) {
            searchSpotify(query);
        } else {
            $("#search-suggestions").hide();
        }
    });
    // Event handler for search suggestion click
    $(document).on("click", ".search-suggestion", function () {
        var suggestionText = $(this).text();
        $("#search-input").val(suggestionText);
        $("#search-suggestions").hide();
    });
});
