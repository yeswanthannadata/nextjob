;(function (angular) {
  "use strict";
  angular.module("home")
         .component("home", {

           "templateUrl": "/js/home/home.html",
           "controller"  : ["$rootScope", "Session", "$http", "$scope", "$state","DTOptionsBuilder", "DTColumnBuilder", "$timeout",

            function ($rootScope, Session,$http, $scope, $state, DTOptionsBuilder, DTColumnBuilder, $timeout) {

                var self = this;
                this.user = Session.get();
                var isAgent;

                if (this.user.roles.indexOf("Agent") >= 0) {

                  isAgent = true;
                    this.user.role = "Agent";
                    if (this.user.roles.indexOf("Admin") >= 0) {

                        this.user.role = "Admin";
                    }
                } else {

                    this.user.role = "SPOC";
                }

                function declare_info(){
                    console.log("in declare");
                    self.info = {

                        "fname"  : "",
                        "lname"  : "",
                        "date"   : "",
                        "mobile" : "",
                        "email"  : "",
                        "status" : "",
                        "remarks": ""
                    }
                }

                this.isAgent = isAgent;

                self.JDs =[];
                self.JDdes ={};
                self.locations = [];
                self.dtInstance = {};
                var candidate_url = "/api/candidates/?jd=";
                var add_candidate_url = "/api/add_candidate/?fname=";
                var jds_url = "/api/jds";
                var update_candidate_url = "/api/update_candidate/?fname=";
                var status_dropdown ='/api/status_dropdown';
                var delete_candidate_url = '/api/delete_candidate/';
                var history_url         = '/api/get_candidate_log/?id=';
                var flag = 1;
                var id_to_delete = [];
                self.status_options = [];
                declare_info();

                //show message popup code

                var show_msg = function(msg){
                    var timer = 0;
                    $("#notification .msg-body").text(msg);
                    var $that = $("#notification").removeClass("hide").slideDown();
                    if(arguments[1]){
                        timer = window.setTimeout(function(){
                            $that.slideUp();
                        },arguments[1]);
                    } 
                },
                hide_msg = function(){
                    $("#notification").addClass("hide").slideUp();
                };

                $("#notification .close").click(function(){
                hide_msg();
                });


                //get candidate status options for dropdown
                $http.get(status_dropdown).success(function(data, status) {
                    self.status_options = data['result'];
                });

                //date picker in home page
                self.date_filter = date_filter;

                function date_filter(){

                    console.log(self.myDate);
                    var jd = $( ".drop_down option:selected" ).val().replace('number:', '');
                    var date_type  = $('input[name=date_filter]:checked').val();
                    self.dtOptions = DTOptionsBuilder.fromSource(candidate_url + jd + '&filter_date=' + self.myDate + '&date_type=' + date_type)
                        .withOption('stateSave', true)
                        .withPaginationType('full_numbers')
                        .withDOM('lfrtip')
                        .withOption('order', [1, 'desc'])
                        .withOption('fnRowCallback', rowCallback)
                        .withLanguage({
                            "sLengthMenu":     "Show _MENU_ ",
                        })
                        .withButtons([
                                'print',
                                'excel'
                        ]);

                }

                //date reset on change jd dropdown
                self.jd_date_reset = jd_date_reset;
                function jd_date_reset(){

                    self.myDate = null;
                    //self.$broadcast('md-calendar-change', self.myDate);
                }

                //date reset on change radio button
                $('body').on('change', 'input[type=radio][name=date_filter]', function(){

                    console.log("changed");
                    self.myDate = null;
                });

                //checkbox delete button
                $('body').on('click', '.delete_click', function(){

                    if(id_to_delete.length != 0){

                        $('#confirm_delete_modal').modal();
                        $('.modal-footer').on('click', '.confirm_delete_button', function(){
                        //var r = confirm("Are you sure you want to delete the selected candidates ? ");

                            $http.defaults.headers.post["Content-Type"] = "application/x-www-form-urlencoded";
                            var data = $.param({
                                id_to_delete_json: JSON.stringify({
                                    id_to_delete
                                })
                            });

                            $http.post(delete_candidate_url, data).success(function(data, status) {

                                            show_msg("Deleted Successfully",1500);
                                            var jd = $( ".drop_down option:selected" ).val().replace('number:', '');
                                            self.dtOptions = DTOptionsBuilder.fromSource(candidate_url + 100)
                                                               .withOption('order', [1, 'desc'])
                                                               .withOption('fnRowCallback', rowCallback)
                                                               .withDOM('lfrtip')
                                                               .withLanguage({
                                                                    "sLengthMenu":     "Show _MENU_ ",
                                                                })
                                                               .withButtons(['print','excel']);
                                            self.dtOptions = DTOptionsBuilder.fromSource(candidate_url + jd)
                                                               .withOption('order', [1, 'desc'])
                                                               .withOption('fnRowCallback', rowCallback)
                                                               .withDOM('lfrtip')
                                                               .withLanguage({
                                                                    "sLengthMenu":     "Show _MENU_ ",
                                                                })
                                                               .withButtons(['print','excel']);
                                    $timeout(function() {

                                        var refresh_btn = document.getElementById('refresh_btn');
                                        console.log(refresh_btn);
                                        angular.element(refresh_btn).triggerHandler('click');
                                    }, 0);
                            });
                        });
                    }//if
                });

                //modal close click
                $('body').on('click', '.close_modal', function(){
                    console.log("clik");
                    $('.form-group').removeClass('has-error'); 
                });


                function rowCallback(nRow, aData, iDisplayIndex, iDisplayIndexFull) {

                    //declare_info();
                    $('td', nRow).unbind('click');
                    $(nRow).on('click', 'td:not(\'.check__box\')', function() {
                        $(".status_dropdown").show();
                        $(".success_message").hide();
                        $scope.$apply(function() {
                            self.tableClickHandler(aData);
                            //declare_info();
                        });
                    });

                    //check box click function
                    $(nRow).on('click', '.check_box', function() {

                        console.log("clicked checkbox");
                        var id = $(this).attr('data-check_id');
                        if($(this).is(":checked")){
                            console.log("checked");
                            id_to_delete.push(id);
                        }
                        else{

                            id_to_delete = jQuery.grep(id_to_delete, function(value) {

                                return value != id;
                            });
                        }
                        console.log(id_to_delete);

                    });



                    return nRow;
                }

                $http.get(jds_url).success(function(data, status) {

                        self.JDdefault = data['result'][0]['id'];
                        self.dtInstance.changeData(candidate_url + self.JDdefault);

                    for (var key in data['result']){

                        self.JDs.push({'id': data['result'][key]['id'], 'name': data['result'][key]['name'] +
                                       " - " + data['result'][key]['location'] + " - " + data['result'][key]['id']});
                        self.JDdes[data['result'][key]['id']] = {};
                        self.JDdes[data['result'][key]['id']]["candidates_required"] = data['result'][key]['candidates_req'];
                        self.JDdes[data['result'][key]['id']]["Location"] = data['result'][key]['location'];
                        self.JDdes[data['result'][key]['id']]["min_experience"] = data['result'][key]['min_experience'];
                        self.JDdes[data['result'][key]['id']]["maximum experience"] = data['result'][key]['max_experience'];
                        self.JDdes[data['result'][key]['id']]["min_salary"] = data['result'][key]['min_salary'];
                        self.JDdes[data['result'][key]['id']]["max_salary"] = data['result'][key]['max_salary'];
                    }

                }).error(function( error){ console.log("error")});

                self.tableData = {};
                var titleHtml = '<img src="/images/delete_bin.svg" class="delete_click" data-toggle="tooltip" '+ 
                                'title="Delete Selected Candidates" />'
                self.tableClickHandler = tableClickHandler;
                self.dtOptions = DTOptionsBuilder.fromSource(candidate_url + 100)
                    .withOption('stateSave', true)
                    .withPaginationType('full_numbers')
                    .withOption('order', [1, 'desc'])
                    .withOption('fnRowCallback', rowCallback)
                    .withDOM('lfrtip')
                    .withLanguage({
                        "sLengthMenu":     "Show _MENU_ ",
                        }) 
                    .withButtons(['print','excel']);

                    console.log(this.user.role);
                    if(this.user.role == 'SPOC'){
                        $('#fileupload').hide();
                        $('.add_candidate_button').hide();
                        $('.or').hide();
                    }


                self.dtColumns = [
                    DTColumnBuilder.newColumn(null).withTitle(titleHtml).notSortable().withClass('check__box')
                    .renderWith(function(data, type, full, meta) {
                        //self.selected[full.id] = false;
                        return '<input type="checkbox"class="check_box" ng-model="$ctrl.isChecked_' + data.id + '"' +  ' data-check_id = '+ data.id + ' >';
                    }),
                    DTColumnBuilder.newColumn('created_at').withTitle('Submitted'),
                    DTColumnBuilder.newColumn('name').withTitle('Candidate'),
                    DTColumnBuilder.newColumn('walk_in_date').withTitle('Scheduled'),
                    DTColumnBuilder.newColumn('mobile_number').withTitle('Mobile'),
                    DTColumnBuilder.newColumn('email_id').withTitle('E-mail'),
                    DTColumnBuilder.newColumn('status').withTitle('Status'),
                    DTColumnBuilder.newColumn('agent_name').withTitle('Agent'),
                    DTColumnBuilder.newColumn('id').withTitle('ID').withClass('hide'),
                    DTColumnBuilder.newColumn('remarks').withTitle('Remarks').withClass('hide'),
                ];

                //on click each row
                function tableClickHandler(info) {

                    //history block
                    var history_content      = "<h4 style='border-bottom:1px solid green'>Recent Actions</h4>";

                    $http.get(history_url + info.id).success(function(data, status){
                        console.log(data);
                        for (var key in data){
                            history_content += "<h5 style='margin-bottom:1px; margin-top:5px'><strong>" + key + "</strong></h5>" +
                                               "<p style='border-bottom:1px dotted green; font-size:12px'>On " + data[key]['modified_at'] +
                                               "<br/>By " + data[key]['agent'] + "<br/><span style='font-size:10px; font-style:italic'>" + 
                                                data[key]['remarks'] + "</span></p>"
                        }
                        $('.history_content').html(history_content);
                    }).error(function( error){ console.log("error")});

                    $('.form_col').removeClass('col-md-12').addClass('col-md-8');
                    $('#submit').css({'bottom':'-50px', 'right':'-140px'});
                    $('.history_col').css('display','block');

                    console.log(info);
                    $('#candidate_modal').modal();
                    $('.lname').attr('data-mode','a');
                    $('.modal-title').html('Edit Candidate');
                    var name = info.name.split('  ');
                    self.info.fname = name[0];
                    self.info.lname = name[1];
                    //$('.fname').val(name[0]);
                    //$('.lname').val(name[1]);
                    $('.fname').attr('data-id', info.id);
                    var date = info.walk_in_date.split("/");
                    self.info.date = new Date(date[2], date[0]-1, date[1]);
                    self.info.mobile = parseInt(info.mobile_number);
                    self.info.email = info.email_id;
                    self.info.remarks = info.remarks;
                    self.info.status  = info.status
                    
                    //$('.date').val(date[2]+"-"+date[0]+"-"+date[1]);
                    //$('.mobile').val(info.mobile_number);
                    //$('.email').val(info.email_id);
                    //$('.remarks').val(info.remarks);
                    //$('.location').val(info.location);

                    /*$('[name=status] option').filter(function() {
                        return ($(this).text() == info.status);
                    }).prop('selected', true);*/

                }

                //on click ADD
                self.add_candidate = add_candidate;
                function add_candidate() {
                    $(".status_dropdown").hide();
                    $('.history_col').css('display','none');
                    $('#submit').css({'bottom':'-50px', 'right':'50px'});
                    $('.form_col').removeClass('col-md-8').addClass('col-md-12');
                    $('.lname').attr('data-mode','add');
                    declare_info();
                    $('.fm').removeClass('has-error');
                    $('.dat').removeClass('has-error');
                    $('.mob').removeClass('has-error');
                    $('.em').removeClass('has-error');
                    $('.form-group').removeClass('has-error');
                    /*$('.fname').val('');
                    $('.lname').val('');
                    $('.date').val('');
                    $('.mobile').val('');
                    $('.email').val('');
                    $('.location').val('');
                    $('.remarks').val('');*/
                    //$("select[name='status']").val("Scheduled");
                    $('.modal-title').html('Add Candidate');
                    $('.success_message').hide();
                    
                    $('#candidate_modal').modal();
                }

                //edit details
                this.edit_data = function (info) {

                    var mode = $('.lname').attr('data-mode');
                    if(mode == 'add'){

                            var jd = $( ".drop_down option:selected" ).val().replace('number:', '');
                            $http.get(add_candidate_url + info.fname + '&lname=' + info.lname + '&date=' + info.date + '&jd=' + jd +
                              '&email=' + info.email + '&mobile=' + info.mobile + '&remarks=' +
                              info.remarks).success(function(data, status) {

                                if(data['msg']=="Duplicate Mobile number"){
                                    //alert("Mobile number already exists");
                                    $(".success_message").removeClass('alert-success').addClass('alert-danger');
                                    $(".success_message").html("Mobile number already exists in this JD");
                                    $(".success_message").show();
                                }
                                else{
                                    $(".success_message").removeClass('alert-danger').addClass('alert-success');
                                    $(".success_message").html("Added Successfully");
                                    $(".success_message").show();
                                    $("#text").val('');
                                    $("#date").val('');
                                    var jd = $( ".drop_down option:selected" ).val().replace('number:', '');
                                    self.dtOptions = DTOptionsBuilder.fromSource(candidate_url + 100)
                                                       .withOption('order', [1, 'desc'])
                                                       .withOption('fnRowCallback', rowCallback)
                                                       .withDOM('lfrtip')
                                                       .withLanguage({
                                                             "sLengthMenu":     "Show _MENU_ ",
                                                        }) 
                                                       .withButtons(['print','excel']);
                                    self.dtOptions = DTOptionsBuilder.fromSource(candidate_url + jd)
                                                       .withOption('order', [1, 'desc'])
                                                       .withOption('fnRowCallback', rowCallback)
                                                       .withDOM('lfrtip')
                                                       .withLanguage({
                                                            "sLengthMenu":     "Show _MENU_ ",
                                                        })
                                                       .withButtons(['print','excel']);
                                }
                                declare_info();
                                $('.fm').removeClass('has-error');
                                $('.dat').removeClass('has-error');
                                $('.mob').removeClass('has-error');
                                $('.em').removeClass('has-error');
                                $('.form-group').removeClass('has-error');

                            }).error(function( error){ console.log("error")});
                    }
                    else{

                        var id = $('.fname').attr('data-id');
                        console.log(info);
                        $http.get(update_candidate_url + info.fname + '&lname=' + info.lname + '&date=' +
                            info.date + '&mobile=' + info.mobile + '&email=' + info.email + '&status=' + info.status + '&id='+
                            id + '&remarks=' + info.remarks)
                            .success(function(data, status) {

                                //declare_info();
                                console.log(data);
                                $(".success_message").removeClass('alert-danger').addClass('alert-success');
                                $(".success_message").html("Updated Successfully");
                                $(".success_message").show();
                                var jd = $( ".drop_down option:selected" ).val().replace('number:', '');
                                self.dtOptions = DTOptionsBuilder.fromSource(candidate_url + jd)
                                                .withOption('order', [1, 'desc'])
                                                .withDOM('lfrtip')
                                                .withOption('fnRowCallback', rowCallback)
                                                .withLanguage({
                                                      "sLengthMenu":     "Show _MENU_ ",
                                                })
                                                .withButtons(['print','excel']);
                            }).error(function( error){ console.log("error")});
                   }

                            $timeout(function() {
                                var refresh_btn = document.getElementById('refresh_btn');
                                console.log(refresh_btn);
                                angular.element(refresh_btn).triggerHandler('click');
                            }, 0);


                };


                //refresh

                self.refresh = function(){
                    var jd = $( ".drop_down option:selected" ).val().replace('number:', '');
                    console.log(jd);
                    self.dtInstance.reloadData();
                    //location.reload();
                /*self.dtOptions = DTOptionsBuilder.fromSource(candidate_url + jd)
                    .withOption('stateSave', true)
                    .withPaginationType('full_numbers')
                    .withDOM('lfrtip')
                    .withOption('order', [1, 'desc'])
                    .withOption('fnRowCallback', rowCallback)
                    .withLanguage({
                        "sLengthMenu":     "Show _MENU_ ",
                        })
                    .withButtons(['print','excel']);*/

                };

            }]
        });
}(window.angular));
