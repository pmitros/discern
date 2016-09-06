var get_essay_template = function(data) {
    /*
    Render an essay writing template for a given problem
     */
    var target = $(data.target).parent();
    //get needed info for the essay template
    var problem_id = parseInt(target.data('problem_id'));
    var prompt = target.data('prompt');
    var name = target.data('name');

    //find the template and container
    var essay_template = $('#essay-template').html();
    var essay_container = $('#essay-container');

    var rendered_essay_template = _.template(essay_template,{prompt : prompt, problem_id : problem_id, name: name})

    //render the essay writing template
    essay_container.empty();
    essay_container.html(rendered_essay_template);
    $('#essay-save').click(save_essay);
}

var save_essay = function(data) {
    /*
    Post a given essay to the api and save it
     */
    var target_btn = $(data.target);
    var form = target_btn.parent().parent();
    //scrape needed data from the form
    var problem_id = parseInt(form.data("problem_id"))
    var essay_text = form.find('#essay-text').val()
    var api_url = $('#model_name').attr("url") + "/";
    //generate post data dict, and fill in some needed attributes manually (these fields are needed by the api)
    post_data = {
        essay_text : essay_text,
        essay_type : "train",
        problem : problem_id,
        additional_predictors : [],
        has_been_ml_graded : false
    }
    //post the data to the api
    $.ajax({
        type: "POST",
        url: api_url,
        data: { action: "post", model: 'essay', data : JSON.stringify(post_data)}
    }).done(get_courses);
}

$(function(){
    var tokenValue = $.cookie('problemgradercsrftoken');

    $.ajaxSetup({
        data: {csrfmiddlewaretoken: tokenValue },
        headers: {'X-CSRF-Token': tokenValue}
    });
    get_courses()
})