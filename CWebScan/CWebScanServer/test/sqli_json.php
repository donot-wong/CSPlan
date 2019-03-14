<?php
	//连接数据库
	$con = new mysqli('127.0.0.1','root','654321','mysql','3306');
	// $con = new mysqli('127.0.0.1','root','654321','mysql','3306');
	
	if(mysqli_connect_errno()){
	    echo '数据库连接错误！错误信息是：'.mysqli_connect_error();
	    exit;
	}
	$data = json_decode(file_get_contents('php://input'));
	$user = $data->user;
	//准备SQL语句
	$sql = "select * from mysql.user where user='" . $user . "'";
	//echo $sql;
	//执行SQL语句
	$query = $con->query($sql);
	
	// var_dump($query->fetch_array());	
	while($row = $query->fetch_array()){
	    echo $row['User'],'<br>';
	}
	
	//释放资源
	$query->close();
	
	//关闭连接
	$con->close();
?>