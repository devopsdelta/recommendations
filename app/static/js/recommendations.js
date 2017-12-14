$(function () {

        // ****************************************
        //  U T I L I T Y   F U N C T I O N S
        // ****************************************

        // Updates the form with data from the response
        function update_form_data(res) {
            $("#product_id").val(res.product_id);
            $("#rec_product_id").val(res.rec_product_id);
            $("#rec_type_id").val(res.rec_type_id);
            $("#weight_id").val(res.weight);

            if (res.available == true) {
                $("#rec_available").val("true");
            } else {
                $("#rec_available").val("false");
            }
        }

        // ****************************************
        // Create or Update a Recommendation
        // ****************************************

        $("#save-btn").click(function () {
            var rec_id = $("#rec_id").val();
            var verb = "POST"
            var url = "/recommendations"
            var message = "Created"

            if (rec_id != '') {
                verb = "PUT"
                url = "/recommendations/" + rec_id
                message = "Updated"
            }

            var product_id = $("#product_id").val();
            var rec_product_id = $("#rec_product_id").val();
            var rec_type_id = $("#rec_type_id").val();
            var weight_id = $("#weight_id").val();

            var data = {
                "product_id": parseInt(product_id),
                "rec_product_id": parseInt(rec_product_id),
                "rec_type_id": parseInt(rec_type_id),
                "weight": parseFloat(weight_id)
            };

            var ajax = $.ajax({
                type: verb,
                url: url,
                contentType:"application/json",
                data: JSON.stringify(data),
            });

            ajax.done(function(res){
                clear_form_data()
                update_form_data(res)
                flash_message(message)
            });

            ajax.fail(function(res){
                flash_message(res.responseJSON.message)
            });
        });

        // ****************************************
        // Retrieve a Recommendation
        // ****************************************

        $("#retrieve-btn").click(function () {

            var rec_id = $("#rec_id").val();

            var ajax = $.ajax({
                type: "GET",
                url: "/recommendations/" + rec_id,
                contentType:"application/json",
                data: ''
            })

            ajax.done(function(res){
                update_form_data(res)
                flash_message("Successfully retrieved recommendation: " + rec_id)
            });

            ajax.fail(function(res){
                clear_form_data()
                flash_message(res.responseJSON.message)
            });

        });

        // ****************************************
        // Clear the form
        // ****************************************

        $("#clear-btn").click(function () {
            $("#rec_id").val("");
            clear_form_data()
        });

        // ****************************************
        // Search for a Recommendation
        // ****************************************

        $("#search-btn").click(function () {

            var product_id = $("#product_id_search").val();
            var type_name = $("#rec_type_name").val();

            var queryString = ""

            if (type_name) {
                queryString += 'type=' + type_name
            }

            if (product_id) {
                if (queryString.length > 0) {
                    queryString += '&product_id=' + product_id
                } else {
                    queryString += 'product_id=' + product_id
                }
            }

            var ajax = $.ajax({
                type: "GET",
                url: "/recommendations?" + queryString,
                contentType:"application/json",
                data: ''
            })

            ajax.done(function(res){
                $("#search_results").empty();
                var html = "<table id='search_results' class='table table-bordered table-striped dataTable'"
                html += " role='grid' aria-describedby='search_result_info'>"
                html += '<thead>'
                html += '<tr role="row">'
                html += '<th class="sorting_asc" tabindex="0" aria-controls="example1 rowspan="1" colspan="1" style="width: 240.8px;" aria-sort="ascending" aria-label="Recommendation Id: activate to sort column descending">Rec Id</th>'
                html += '<th class="sorting" tabindex="0" aria-controls="example1" rowspan="1" colspan="1" style="width: 203.6px;" aria-label="Product Id: activate to sort column ascending">Product Id</th>'
                html += '<th class="sorting" tabindex="0" aria-controls="example1" rowspan="1" colspan="1" style="width: 259.833px;" aria-label="Type: activate to sort column ascending">Type</th>'
                html += '<th class="sorting" tabindex="0" aria-controls="example1" rowspan="1" colspan="1" style="width: 208.433px;" aria-label="Recommended Product Id: activate to sort column ascending">Rec Product Id</th>'
                html += '<th class="sorting" tabindex="0" aria-controls="example1" rowspan="1" colspan="1" style="width: 152.333px;" aria-label="Weight: activate to sort column ascending">Weight</th>'
                html += '<th class="sorting" tabindex="0" aria-controls="example1" rowspan="1" colspan="1" style="width: 200px;" aria-label="Status: activate to sort column ascending">&nbsp;</th>'
                html += '</tr>'
                html += '</thead>'
                html += '<tbody>'

                for(var i = 0; i < res.length; i++) {
                    rec = res[i];
                    row_class = ((i % 2 == 0) ? 'even' : 'odd');
                    var row = "<tr role='row' class='" + row_class + "'>"
                    row += "<td><a href='/recommendations/detail/" + rec.id + "'>" + rec.id + "</a></td>"
                    row += "<td>" + rec.product_id + "</td>"
                    row += "<td>" + rec.rec_type.name + "</td>"
                    row += "<td>" + rec.rec_product_id + "</td>"
                    row += "<td>" + rec.weight + "</td>"
                    row += "<td><button class='btn btn-link' id='edit_" + rec.id + "-btn' onclick='edit_row(" + rec.id + ");'>Edit</button> | "
                    row += "<button class='btn btn-link' id='delete_" + rec.id + "-btn' onclick='confirm_delete(" + rec.id + ");'>Delete</button></td>"
                    row += "</tr>"

                    html += row
                }
                html += '</tbody>'
                html += '</table>'

                $("#search_results").append(html);

                flash_message("Success")
            });

            ajax.fail(function(res){
                flash_message(res.responseJSON.message)
            });

        });
    })

    function confirm_delete(id) {
        var ajax = $.ajax({
            type: "DELETE",
            url: "/recommendations/" + id,
            contentType:"application/json",
            data: '',
        })

        ajax.done(function(res){
            flash_message("Deleted")
            if(!json.error) location.reload(true);
        });

        ajax.fail(function(res){
            flash_message("Server error!")
        });
    
    }

    function edit_row(id) {        
        var ajax = $.ajax({
            type: "GET",
            url: "/recommendations/" + id,
            contentType:"application/json",
            data: ''
        })

        ajax.done(function(res){
            clear_form_data()
            $("#rec_id").val(res.id)
            $("#product_id").val(res.product_id);
            $("#rec_product_id").val(res.rec_product_id);
            $("#rec_type_id").val(res.rec_type_id);
            $("#weight_id").val(res.weight);

            if (res.available == true) {
                $("#rec_available").val("true");
            } else {
                $("#rec_available").val("false");
            }

            flash_message("Successfully retrieved recommendation: " + id)
        });

        ajax.fail(function(res){
            clear_form_data()
            flash_message(res.responseJSON.message)
        });

    }

    function activate(id) {
        var ajax = $.ajax({
            type: "PUT",
            url: "/recommendations/activate/" + id,
            contentType:"application/json",
            data: '',
        })

        ajax.done(function(res){
            flash_message("Activated")
            location.reload();
        });

        ajax.fail(function(res){
            flash_message("Server error!")
        });
    
    }

    function deactivate(id) {
        var ajax = $.ajax({
            type: "PUT",
            url: "/recommendations/deactivate/" + id,
            contentType:"application/json",
            data: '',
        })

        ajax.done(function(res){
            flash_message("Deactivated")
            location.reload();
        });

        ajax.fail(function(res){
            flash_message("Server error!")
        });
    
    }

    // Updates the flash message area
    function flash_message(message) {
        $("#flash_message").empty();
        $("#flash_message").append(message);
    }

    /// Clears all form fields
    function clear_form_data() {
        $("#product_id").val('');
        $("#rec_product_id").val('');
        $("#rec_type_id").val('1');
        $("#weight_id").val('');
    }
