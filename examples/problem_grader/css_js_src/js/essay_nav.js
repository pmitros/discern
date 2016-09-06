var get_courses = function() {
    /*
     Gets a course listing that allows us to navigate to problems
     */
    //empty all sections
    $('#problem_nav').empty()
    $('#course_nav').empty()
    $('#essay-container').empty()

    //get the course listing from the api
    var api_base = $('#model_name').attr("url");
    $.ajax({
        type: "GET",
        url: api_base,
        data: { action: "get", model: "course" }
    }).done(render_course_nav);
}

var get_problems = function(course_id) {
    /*
     Get a problem listing for a given course
     */
    var api_base = $('#model_name').attr("url");
    $.ajax({
        type: "GET",
        url: api_base,
        data: { action: "get", model: "problem" }
    }).done(render_problem_nav_wrapper(course_id));
}

var render_problem_nav_wrapper = function(course_id) {
    /*
     Wrap the render_problem_nav function so that we can pass in course_id
     */
    var render_problem_nav = function (data) {
        /*
         Render the problems for a given course
         */
        //parse the api problem listing data
        data = $.parseJSON(data);
        problems = new Array();
        //if the problem is attached to the course specified by course_id, append it
        for(var z=0; z< data.length ; z++) {
            var problem = data[z]
            //loop through all of the courses that the problem is associated with
            for(var i=0;i< problem.courses.length;i++){
                //if a given problem is attached to this course, add it to the array
                var course_split= problem.courses[i].split("/");
                if(parseInt(course_split[5])==parseInt(course_id)){
                    problems.push(problem);
                }
            }
        }
        //get and render the problem nav template
        var problem_nav_template = $("#problem-nav-template").html()
        var rendered = _.template(problem_nav_template,{problems : problems, course_id : course_id})
        var problem_nav = $("#problem_nav")
        problem_nav.empty()
        problem_nav.html(rendered)

        //register problem select click event
        $('.problem-select').click(get_essay_template);
    };
    return render_problem_nav
}

var render_course_nav = function(data) {
    /*
     Render top level course navigation
     */
    var add_template = $( "#course-nav-template" ).html();
    var course_nav = $('#course_nav')
    data = $.parseJSON(data);
    course_nav.html(_.template(add_template,{courses : data}))
    $('.course-select').click(get_problem_nav);
}

var get_problem_nav = function(data) {
    /*
     Render problem navigation once a course has been selected
     */
    var target = $(data.target).parent();
    var course_id = parseInt(target.data('course_id'))
    get_problems(course_id)
}