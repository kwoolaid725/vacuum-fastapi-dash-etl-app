UPDATE test_details
SET test_measure
= (SELECT description FROM test_measures WHERE test_measures.id = test_details.test_measure_id);