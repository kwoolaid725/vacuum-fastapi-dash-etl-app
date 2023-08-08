$(document).ready(function(){
    // $("#kt_modal_new_target_submit").click(function() {
    //     $('#search_assigned1').attr('name', 'assigned1');
    // });
    //
    //   $("#kt_modal_new_target_submit").click(function() {
    //     $('#search_assigned2').attr('name', 'assigned2');
    // });
      $('#User_Search_List li:gt(4)').remove();
      $('#User_Search_List2 li:gt(4)').remove();
      $('#tags').keyup(function() {
            $('#tags').val();
      });
});


