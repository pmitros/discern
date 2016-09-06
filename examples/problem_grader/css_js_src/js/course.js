var get_models = function(api_url, model_type, callback) {
    /*
    Get the course instance listing from the api and perform a callback to render
     */
    $.ajax({
        type: "GET",
        url: api_url,
        data: { action: "get", model: model_type }
    }).done(callback);
 }

var render_course = function(data) {
    /*
    Called by get_models to render the course list
    data - json data from the api
     */
    //find and empty the html container
    var model_data = $("#model_container");
    model_data.empty();
    //the data is in json format, so load it
    data = $.parseJSON(data);
    //get the item and container templates (we will write to them using underscore)
    var item_template = $( "#course-item-template" ).html();
    var container_template = $( "#course-list-template" ).html();
    var courses = new Array();
    //loop through each course and render an item template for it
    for (var i = 0; i < data.length; i++) {
        var elem = data[i];
        var mod_course_name = elem.course_name.replace(/ /g, "_");

        var elem_dict = {
            name : elem.course_name,
            href : elem.id + mod_course_name,
            user_count : elem.users.length,
            problem_count: elem.problems.length,
            modified : new Date(Date.parse(elem.modified)),
            created: new Date(Date.parse(elem.created)),
            id : elem.id
        }
        //put each rendered course into an array
        courses.push(_.template(item_template,elem_dict));
    }
    var template_data = {
        courses: courses
    };
    //add all of the templates into a container and render it
    model_data.append(_.template(container_template,template_data))
    add_course_button()
    //Register some click events
    $('#create-course').click(create_course);
    $('.delete-course').click(delete_course);
    $('.show-problems').click(get_problem);
}

var get_problem = function(target) {
    /*
    When the "show problems" button is clicked, redirect to the problems view
     */
    var target_btn = $(target.target);
    var form = target_btn.parent().parent().parent();
    var inputs = form.find('.accordion-toggle')
    var course_id = inputs.data('elem_id')
    //redirect the user to the appropriate problems page
    window.location.href = "/grader/problem/?course_id=" + course_id;
}

var add_course_button = function() {
    /*
    Add the "add course" link to the listing
     */
    var model_add = $("#model_add")
    model_add.empty()
    var add_template = $( "#course-add-template" ).html();
    var add_dict = {
        name : "Add a course",
        href: "course-add"
    }
    model_add.html(_.template(add_template,add_dict))
}

var get_course_items = function(model_type) {
    /*
    Get all course items.  Called on page load.
    model_type - "course" in this case
     */
    var api_base = $('#model_name').attr("url");
    switch(model_type)
    {
        case "course":
            callback = render_course;
            break;
    }
    get_models(api_base, model_type, callback)
}

var delete_course = function(target) {
    /*
    Calls the api to delete a course
     */
    var target_btn = $(target.target);
    var data = target_btn.parent();
    var id = data.data('elem_id')
    var api_url = $('#model_name').attr("url") + "/";
    $.ajax({
        type: "POST",
        url: api_url,
        data: { action: "delete", model: 'course', id : id}
    }).done(get_model_type_and_items);
}

var create_course = function(target) {
    /*
    Calls the api to create a course
     */
    var target_btn = $(target.target);
    //scrape needed data from the targeted form
    var form = target_btn.parent().parent().parent();
    var inputs = form.find('input')
    var course_name = inputs.val()
    var api_url = $('#model_name').attr("url") + "/";
    post_data = {
        course_name : course_name
    }
    $.ajax({
        type: "POST",
        url: api_url,
        data: { action: "post", model: 'course', data : JSON.stringify(post_data)}
    }).done(get_model_type_and_items);
}

var get_model_type_and_items = function() {
    /*
    Called on page load.  Grabs the model type from the html and then fetches a course listing
     */
    var model_type = $('#model_name').attr('model');
    if(model_type!=undefined) {
        get_course_items(model_type)
    }
}

$(function(){
    //Grab the csrf token and send it along with all ajax operations.  Needed by django.
    var tokenValue = $.cookie('problemgradercsrftoken');

    $.ajaxSetup({
        data: {csrfmiddlewaretoken: tokenValue },
        headers: {'X-CSRF-Token': tokenValue}
    });
    get_model_type_and_items()
})