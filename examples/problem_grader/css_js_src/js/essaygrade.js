var toggle_grading_container = function(target) {
    /*
    Shows or hides the grading container based on user click
     */
    var target = $(target.target);
    var container = target.parent();
    var grading_container = container.find(".grading-container");
    if(grading_container.is(":visible")) {
        grading_container.hide();
    } else {
        grading_container.show();
    }

}

var render_essay_wrapper = function(prompt, problem_id) {
    /*
    Wraps the render_essay function so that prompt and problem_id can be passed in
     */
    var render_essay = function(data) {
        /*
        Renders an essay and allows it to be graded, and for past grades to be viewed
         */
        //empty out the container
        var model_data = $("#essay-container");
        model_data.empty();
        //parse the json data
        data = $.parseJSON(data);

        //get the needed templates
        var item_template = $( "#essay-item-template" ).html();
        var container_template = $( "#essay-list-template" ).html();
        var rubric_list_template = $('#rubric-list-template').html();
        var essaygrades_template = $('#essay-grades-template').html();
        var essaygrade_tab_template = $('#essay-grade-tab-template').html();
        var essaygrade_detail_template = $('#essay-grade-detail-template').html();

        var essays = new Array();

        //loop through each essay that was retrieved from the api
        for (var i = 0; i < data.length; i++) {
            var essaygrade_tabs = new Array();
            var essaygrade_details = new Array();
            var elem = data[i];
            var essay_name = "Essay with id " + elem.id.toString();
            var mod_essay_name = essay_name.replace(/ /g, "_");
            var essaygrade_data = elem.essaygrades_full
            //loop through each essaygrade attached to the essay
            for (var z = 0; z < essaygrade_data.length; z++) {

                //extract needed values from the data
                essaygrade_rubric = essaygrade_data[z]['rubric']
                essaygrade_href = "Essaygrade with id" + essaygrade_data[z]['id']
                essaygrade_href = essaygrade_href.replace(/ /g, "_");
                essaygrade_type = essaygrade_data[z].grader_type;
                var essaygrade_dict = {
                    href : essaygrade_href,
                    rubrics : essaygrade_rubric,
                    type : essaygrade_type
                }
                //render the tab and the detail view for each essaygrade
                var essaygrade_tab = _.template(essaygrade_tab_template,essaygrade_dict);
                var essaygrade_detail = _.template(essaygrade_detail_template,essaygrade_dict);

                //add the tabs and details to the list
                essaygrade_tabs.push(essaygrade_tab);
                essaygrade_details.push(essaygrade_detail);
            }
            //render the full essaygrade html using the pieces
            var essaygrades_html = _.template(essaygrades_template,{tabs : essaygrade_tabs, details : essaygrade_details});

            //render the essay using this data
            var elem_dict = {
                name : essay_name,
                prompt : prompt,
                href : mod_essay_name,
                modified : new Date(Date.parse(elem.modified)),
                created: new Date(Date.parse(elem.created)),
                id : elem.id,
                essay_text : elem.essay_text,
                rubric : _.template(rubric_list_template,{rubrics : elem.rubric}),
                essaygrades : essaygrades_html
            }
            var problem = elem.problem
            var problem_split=problem.split("/");
            //if the problem id matches the user selected problem, add the problem to the essay list
            if(parseInt(problem_split[5])==problem_id){
                essays.push(_.template(item_template,elem_dict));
            }
        }
        var template_data = {
            essays: essays
        };
        //render the full template for all the essays
        model_data.append(_.template(container_template,template_data));

        //hide the grading container initially
        var grading_container = $('.grading-container');
        grading_container.hide();

        //register click events
        $('.grade-essay').click(toggle_grading_container);
        $('.create-essaygrade').click(save_essaygrade);
    }
    return render_essay
}

var get_essay_template = function(data) {
    /*
    Get a list of essays.  Function naming needs to be consistent with essay.js for essay_nav.js to work.
     */
    var target = $(data.target).parent();
    var problem_id = parseInt(target.data('problem_id'));
    var prompt = target.data('prompt');

    var api_base = $('#model_name').attr("url");
    $.ajax({
        type: "GET",
        url: api_base,
        data: { action: "get", model: "essay" }
    }).done(render_essay_wrapper(prompt, problem_id));
}

var save_essaygrade = function(data) {
    /*
    Save the grade for a given essay.
     */
    var target_btn = $(data.target);
    var grading_container = target_btn.parent().parent();
    //extract feedback
    var feedback = grading_container.find('.essay-feedback').val()
    var rubric_scores = new Array();
    var rubric_item_selects = grading_container.find('.rubric-item-select')
    var essay_id = grading_container.parent().parent().parent().find('.accordion-toggle').data('elem_id')
    //for each rubric item, pick 1 if it was checked, and 0 if it was not
    for(var i=0;i < rubric_item_selects.length ; i++) {
        var item_score = 0
        if($(rubric_item_selects[i]).is(':checked')) {
            item_score = 1
        }
        rubric_scores.push(item_score)
    }
    var api_url = $('#model_name').attr("url") + "/";
    //construct the post data dictionary.  Manually add in several values that are required by the API, but don't need to be user surfaced.
    post_data = {
        target_scores: JSON.stringify(rubric_scores),
        essay : essay_id,
        confidence : 1,
        feedback: feedback,
        success: true,
        grader_type: "IN",
        premium_feedback_scores: JSON.stringify("[]"),
        annotated_text: ""
    }
    $.ajax({
        type: "POST",
        url: api_url,
        data: { action: "post", model: 'essaygrade', data : JSON.stringify(post_data)}
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