var get_models = function(api_url, model_type, callback) {
    /*
     Get the problem instance listing from the api and perform a callback to render
     */
    $.ajax({
        type: "GET",
        url: api_url,
        data: { action: "get", model: model_type }
    }).done(callback);
}

var render_problem = function(data) {
    /*
     Called by get_models to render the problem list
     data - json data from the api
     */
    //find and empty the html container
    var model_data = $("#model_container");
    model_data.empty();
    //Load the json data
    data = $.parseJSON(data);
    //find all needed templates
    var item_template = $( "#problem-item-template" ).html();
    var container_template = $( "#problem-list-template" ).html();
    var rubric_list_template = $('#rubric-list-template').html();
    //get the course id from the html
    var matching_course_id = parseInt($("#model_name").data("course_id"))
    var problems = new Array();
    //render the problem item templates
    for (var i = 0; i < data.length; i++) {
        var elem = data[i];
        //need to replace spaces in the problem name
        var mod_problem_name = elem.name.replace(/ /g, "_");

        var elem_dict = {
            name : elem.name,
            prompt : elem.prompt,
            href : elem.id + mod_problem_name,
            modified : new Date(Date.parse(elem.modified)),
            created: new Date(Date.parse(elem.created)),
            id : elem.id,
            rubric : _.template(rubric_list_template,{rubrics : elem.rubric}),
            course_count: elem.courses.length,
            essay_count : elem.essays.length
        }
        //only use problems that match the course_id in the url
        for(var z=0; z< elem.courses.length ; z++) {
            var course = elem.courses[z]
            var course_split=course.split("/");
            if(parseInt(course_split[5])==matching_course_id){
                //Add in rendered problem templates to the problems array
                problems.push(_.template(item_template,elem_dict));
            }
        }
    }
    var template_data = {
        problems: problems
    };
    //render the container for all the problem items
    model_data.append(_.template(container_template,template_data))
    add_problem_button()

    //register click handlers
    $('#create-problem').click(create_problem);
    $('.delete-problem').click(delete_problem);
    $('#rubricadd').click(add_rubric_option);
}

var add_rubric_option = function(target) {
    /*
    Allow the user to add in rubric options
    target - the add rubric option button that the user has clicked
     */
    var target_btn = $(target.target);
    var rubric_container = target_btn.parent().find('#rubric-item-container');
    //disable all of the existing rubric inputs
    rubric_container.find(".rubric_input").attr('disabled','disabled');
    var rubric_template = $( "#rubric-item-template" ).html();
    var rubric_dict = {
        finished : false
    }
    //add in a new rubric input at the end
    var rubric_html = _.template(rubric_template,rubric_dict)
    rubric_container.append(rubric_html)
}

var add_problem_button = function() {
    /*
    Append the add problem button
     */
    //empty the model_add div
    var model_add = $("#model_add")
    model_add.empty()
    //find templates
    var add_template = $( "#problem-add-template" ).html();
    var rubric_template = $( "#rubric-item-template" ).html();
    var rubric_dict = {
        finished : false
    }
    //render the rubric template
    var rubric_html = _.template(rubric_template,rubric_dict)
    var add_dict = {
        name : "Add a problem",
        href: "problem-add",
        rubric: rubric_html
    }
    //render the add template
    model_add.html(_.template(add_template,add_dict))
}

var get_problem_items = function(model_type) {
    /*
     Get all problem items.  Called on page load.
     model_type - "problem" in this case
     */
    var api_base = $('#model_name').attr("url");
    switch(model_type)
    {
        case "problem":
            callback = render_problem;
            break;
    }
    get_models(api_base, model_type, callback)
}

var delete_problem = function(target) {
    /*
     Calls the api to delete a problem
     */
    var target_btn = $(target.target);
    var data = target_btn.parent();
    var id = data.data('elem_id')
    var api_url = $('#model_name').attr("url") + "/";
    $.ajax({
        type: "POST",
        url: api_url,
        data: { action: "delete", model: 'problem', id : id}
    }).done(get_model_type_and_items);
}

var create_problem = function(target) {
    /*
     Calls the api to create a problem
     */

    //find the target form
    var target_btn = $(target.target);
    var form = target_btn.parent().parent().parent();

    //grab needed fields to post
    var problem_name = form.find('#problem-name-input').val()
    var prompt = form.find('#promptname').val()
    var rubric = form.find("#rubric-item-container")

    //parse the rubric items
    var rubric_items = rubric.find(".rubric-item")
    var options = new Array();
    var course = parseInt($("#model_name").data("course_id"))
    //for each rubric item, get the user input text and selected number of points
    for (var i=0 ; i < rubric_items.length ; i++) {
        if(rubric_items.eq(i).find("select").attr("disabled") == "disabled") {
            options.push({
                points: rubric_items.eq(i).find('select').find(":selected").text(),
                text : rubric_items.eq(i).find('textarea').val()
            })
        }
    }
    var rubric = {
        options : options
    }
    var api_url = $('#model_name').attr("url") + "/";
    post_data = {
        name : problem_name,
        prompt : prompt,
        rubric : rubric,
        course : course,
        premium_feedback_models : "",
        number_of_additional_predictors : 0
    }
    //post the problem
    $.ajax({
        type: "POST",
        url: api_url,
        data: { action: "post", model: 'problem', data : JSON.stringify(post_data)}
    }).done(get_model_type_and_items);
}

var get_model_type_and_items = function() {
    /*
     Called on page load.  Grabs the model type from the html and then fetches a problem listing
     */
    var model_type = $('#model_name').attr('model');
    if(model_type!=undefined) {
        get_problem_items(model_type)
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