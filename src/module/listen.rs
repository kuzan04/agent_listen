use tokio::io::{AsyncReadExt, AsyncWriteExt};
use tokio::net;
use sqlx::{MySqlPool, FromRow};

// use std::time::Duration;

use crate::module::{
    log0::LogHash,
    file::FileDirectory,
    db::{TestConnect, DatabaseCheck}
};

use crate::model::{AgentStore, AgentManage, AgentHistory};

// On test
// use crate::module::test::*;

#[derive(Debug)]
pub struct Recevie {
    pub host: String,
    pub port: String,
}

impl Recevie {
    pub fn new(host: String, port: String) -> Recevie {
        Recevie { host, port }
    }

    fn split_string(input: &str, delimiter: &str) -> Vec<String> {
        input.split(delimiter)
            .map(|s| s.to_string())
            .collect()
    }
    
    async fn test_connect(_type: String, host: String, user: String, passwd: String, database: String) -> String {
        let success: String;
        match _type.parse::<i32>() {
            Ok(t) => { 
                let to_start = TestConnect::new(host, user, passwd, database);
                match t {
                    1 => {
                        if let Ok(res) = to_start.mysql().await {
                            success = res
                        } else {
                            success = "Query details table error.".to_string()
                        }
                    // function on test only!!
                        // if let Ok(res) = time_function(|| to_start.mysql(), "test_connect_mysql").await {
                        //     success = res
                        // } else {
                        //     success = "Query details table error.".to_string()
                        // }
                    },
                    0 => {
                        if let Ok(res) = to_start.oracle().await {
                            success = res
                        } else {
                            success = "Query details table error.".to_string()
                        }
                        // if let Ok(res) = time_function(|| to_start.oracle(), "test_connect_oracle").await {
                        //     success = res
                        // } else {
                        //     success = "Query details table error.".to_string()
                        // }
                    },
                    _ => success = "Hello from Server!".to_string(),
                };
            }
            Err(_) => {
                success = "Failed to read type from client!".to_string()
            }
        };
        success
    }

    fn status_store(query: Vec<AgentStore>, select: String) -> bool {
        let mut result = false;
        let mut i = 0;
        while i != query.len() {
            match &query[i] {
                a if a.code == select => {
                    if a.status == 1 {
                        result = true
                    }
                    i += 1
                },
                _ => i += 1,
            }
        }
        result
    }

    fn set_manage(manager: Vec<AgentManage>, code: String, name: String) -> Result<AgentManage, String> {
        let mut i = 0;
        let mut selected = AgentManage::default();
        while i < manager.len() {
            if manager[i].agm_name == name && manager[i].code == code {
                selected = manager[i].clone();
            }
            i += 1
        }
        if selected == AgentManage::default() {
            Err("Not Found".to_string())
        } else{
            Ok(selected)
        }
    }

    async fn set_history(db: MySqlPool, manager: Vec<AgentManage>, code: String, name: String) -> String { 
        let env_history = Self::split_string(&dotenv::var("TB_HISTORY").unwrap_or_else(|_| "TB_TR_PDPA_AGENT_LISTEN_HISTORY:agm_id".to_string()), ":");
        // function on test only!!
        // let env_history = time_function(|| Self::split_string(&dotenv::var("TB_HISTORY").unwrap_or_else(|_| "TB_TR_PDPA_AGENT_LISTEN_HISTORY:agm_id".to_string()), ":"), "split_string#10");
        let history: Vec<AgentHistory> = sqlx::query(
            format!(
                "SELECT {} FROM {} GROUP BY {}",
                env_history[1].clone(),
                env_history[0].clone(),
                env_history[1].clone()
            ).as_str())
            .fetch_all(&db)
            .await.unwrap()
            .into_iter()
            .map(|row| AgentHistory::from_row(&row).unwrap())
            .collect();
        let selected = Self::set_manage(manager, code, name);
        // function on test only!!
        // let selected = time_function(|| Self::set_manage(manager, code, name), "set_manage");
        match selected {
            Ok(agm) => {
                let mut message = String::new(); // 
                let mut i = 0;
                while i < history.len() {
                    if history[i].agm_id == agm.agm_id {
                        sqlx::query(format!("UPDATE {} SET _get_ = NOW() WHERE {} = ?", env_history[0], env_history[1]).as_str())
                            .bind(agm.agm_id)
                            .execute(&db)
                            .await.unwrap();
                        message = "Success".to_string()
                    }
                    i += 1
                }
                match message.chars().count() {
                    0 => {
                        sqlx::query(format!("INSERT INTO {} ({}) VALUES (?)", env_history[0], env_history[1]).as_str())
                            .bind(agm.agm_id)
                            .execute(&db)
                            .await.unwrap();
                        "Success".to_string()
                    }
                    _ => "Success".to_string()
                }
            },
            Err(err) => format!("[Error] {} agent client from web alltra", err)
        }
    }

    async fn main_task(status: bool, details: Vec<String>, db: MySqlPool) -> String {
        match status {
            true => {
                match details[0].as_str() {
                    "AG1" => {
                        let mut log0_table_all = Self::split_string(
                            &dotenv::var("TB_LOG0").unwrap_or_else(|_| "TB_TR_PDPA_AGENT_LOG0_HASH:device_name, os_name, path, name_file, total_line, value, value_md5, value_sha1".to_string()),
                            ":"
                        );
                        let log0_columns = Self::split_string(&log0_table_all.pop().unwrap(), ",");
                        let log0_table = log0_table_all.pop().unwrap();
                        let content = Self::split_string(&details[details.len() - 1], "|||");
                        match LogHash::new(db, log0_table, log0_columns, content).build().await {
                            Ok(s) => s,
                            Err(e) => e.to_string(),
                        }

                        // function on test only!!
                        // let mut log0_table_all = time_function(|| Self::split_string(
                        //     &dotenv::var("TB_LOG0").unwrap_or_else(|_| "TB_TR_PDPA_AGENT_LOG0_HASH:device_name, os_name, path, name_file, total_line, value, value_md5, value_sha1".to_string()),
                        //     ":"
                        // ), "split_string#1");
                        // let log0_columns = time_function(|| Self::split_string(&log0_table_all.pop().unwrap(), ","), "split_string#2");
                        // let log0_table = log0_table_all.pop().unwrap();
                        // let content = time_function(|| Self::split_string(&details[details.len() - 1], "|||"), "split_string#3");
                        // let mut start = LogHash::new(db, log0_table, log0_columns, content);
                        // match time_function(|| start.build(), "main_log0").await {
                        //     Ok(s) => s,
                        //     Err(e) => e.to_string(),
                        // }
                    },
                    "AG2" => {
                        let mut file_table_all = Self::split_string(
                            &dotenv::var("TB_FILE").unwrap_or_else(|_| "TB_TR_PDPA_AGENT_FILE_DIR:id, device_name, os_name, path, name_file, size".to_string()),
                            ":"
                        );
                        let file_columns = Self::split_string(&file_table_all.pop().unwrap(), ",");
                        let file_table = file_table_all.pop().unwrap();
                        let content = Self::split_string(&details[details.len() - 1], "|||");

                        match FileDirectory::new(
                            db,
                            file_table, 
                            file_columns, 
                            dotenv::var("SOURCINATION").unwrap_or_else(|_| "/home/ftpuser/".to_string()), 
                            dotenv::var("DESTINATION_LOG").unwrap_or_else(|_| "/home/ftpuser/".to_string()), 
                            dotenv::var("DESTINATION_DOC").unwrap_or_else(|_| "/var/pdpa/agent/".to_string()), 
                            content
                        ).build()
                            .await {
                                Ok(s) => s,
                                Err(e) => e.to_string()
                            }
                        // function on test only!!
                        // let mut file_table_all = time_function(|| Self::split_string(
                        //     &dotenv::var("TB_FILE").unwrap_or_else(|_| "TB_TR_PDPA_AGENT_FILE_DIR:id, device_name, os_name, path, name_file, size".to_string()),
                        //     ":"
                        // ), "split_string#4");
                        // let file_columns = time_function(|| Self::split_string(&file_table_all.pop().unwrap(), ","), "split_string#5");
                        // let file_table = file_table_all.pop().unwrap();
                        // let content = time_function(|| Self::split_string(&details[details.len() - 1], "|||"), "split_string#6");
                        // let mut start = FileDirectory::new(
                        //     db,
                        //     file_table, 
                        //     file_columns, 
                        //     dotenv::var("SOURCINATION").unwrap_or_else(|_| "/home/ftpuser/".to_string()), 
                        //     dotenv::var("DESTINATION_LOG").unwrap_or_else(|_| "/home/ftpuser/".to_string()), 
                        //     dotenv::var("DESTINATION_DOC").unwrap_or_else(|_| "/var/pdpa/agent/".to_string()), 
                        //     content
                        // );
                        // match time_function(|| start.build(), "main_file").await {
                        //         Ok(s) => s,
                        //         Err(e) => e.to_string()
                        //     }
                    },
                    "AG3" => {
                        let mut dbc_table_all = Self::split_string(
                            &dotenv::var("TB_DB")
                            .unwrap_or_else(|_| "TB_TR_PDPA_AGENT_DATABASE_CHECK:field_1, field_2, field_3, field_4, field_5, field_6, field_7, field_8, field_9, field_0, from_client".to_string()),
                            ":"
                        );
                        let dbc_columns = Self::split_string(&dbc_table_all.pop().unwrap(), ",");
                        let dbc_table = dbc_table_all.pop().unwrap();
                        let mut content = Self::split_string(&details[details.len() - 1], "|||");

                        // function on test only!!
                        // let mut dbc_table_all = time_function(|| Self::split_string(
                        //     &dotenv::var("TB_DB")
                        //     .unwrap_or_else(|_| "TB_TR_PDPA_AGENT_DATABASE_CHECK:field_1, field_2, field_3, field_4, field_5, field_6, field_7, field_8, field_9, field_0, from_client".to_string()),
                        //     ":"
                        // ), "split_string#7");
                        // let dbc_columns = time_function(|| Self::split_string(&dbc_table_all.pop().unwrap(), ","), "split_string#8");
                        // let dbc_table = dbc_table_all.pop().unwrap();
                        // let mut content = time_function(|| Self::split_string(&details[details.len() - 1], "|||"), "split_string#9");
                        
                        // Convert message from_client and values
                        let from_client = content.remove(1);

                        DatabaseCheck::new(db, from_client, dbc_table, dbc_columns, content.clone());

                        // Beta.
                        content[0].to_string()
                    },
                    _ => {
                        "Failed".to_string()
                    }
                }
            },
            false => "Close".to_string()
        }
    }

    #[allow(unused_must_use)]
    async fn handle_client(mut stream: net::TcpStream, db: MySqlPool) {
        let mut buffer = [0; 1024];
        match stream.read(&mut buffer).await {
            Ok(bytes_read) => {
                // Test only!!
                println!("{}", &buffer[..bytes_read].len());
                //
                // Main Taskprocess.
                let get_response = String::from_utf8_lossy(&buffer[..bytes_read]);
                // Set message to response to client.
                let message: String;
                match get_response {
                    // Statement test connection sql.
                    s if s.contains('|') && !s.contains('#') => {
                        let conv_test = Self::split_string(&s, "|");
                        // Call check type sql.
                        message = Self::test_connect(conv_test[0].to_owned(), conv_test[1].to_owned(), conv_test[2].to_owned(), conv_test[3].to_owned(), conv_test[4].to_owned()).await;
                        // message = time_function(|| Self::test_connect(conv_test[0].to_owned(), conv_test[1].to_owned(), conv_test[2].to_owned(), conv_test[3].to_owned(), conv_test[4].to_owned()), "test_connect").await;
                        if let Err(error) = stream.write_all(message.as_bytes()).await {
                            println!("Failed to write to stream: {}", error);
                        }
                    },
                    // Statement main task process agent.
                    s if s.contains('#') => {
                        // Get query from agent store to check status.
                        let store: Vec<AgentStore> = sqlx::query("SELECT * FROM TB_TR_PDPA_AGENT_STORE")
                            .fetch_all(&db)
                            .await.unwrap()
                            .into_iter()
                            .map(|row| AgentStore::from_row(&row).unwrap())
                            .collect();
                        // Get query from agent manage to insert history.
                        let manager: Vec<AgentManage> = sqlx::query("SELECT pam.agm_id, pam.agm_name, pas.code FROM TB_TR_PDPA_AGENT_MANAGE as pam JOIN TB_TR_PDPA_AGENT_STORE as pas ON pam.ags_id = pas.ags_id")
                            .fetch_all(&db)
                            .await.unwrap()
                            .into_iter()
                            .map(|row| AgentManage::from_row(&row).unwrap())
                            .collect();
                        // Convert message AG # Details to Vector.
                        let response = Self::split_string(&s, "#");
                        // Get AG_NAME after success.
                        let result = Self::main_task(Self::status_store(store, response[0].clone()), response.clone(), db.clone()).await;
                        // function on test only!!
                        // let result = time_function(|| Self::main_task(Self::status_store(store, response[0].clone()), response.clone(), db.clone()), "main_task").await;
                        // Set message to response client.
                        Self::set_history(db.clone(), manager, response[0].to_owned(), result).await;
                        // function on test only!!
                        // time_function(|| Self::set_history(db.clone(), manager, response[0].to_owned(), result), "set_history").await;
                        // shutdown mysql.
                        db.close();
                        // if let Err(error) = stream.write_all(message.as_bytes()).await {
                        //     println!("Failed to write to stream: {}", error);
                        // }
                    },
                    _ => {
                        message = "Failed unknow type agent. Please check token, .env, or api from alltra again!!".to_string();
                        if let Err(error) = stream.write_all(message.as_bytes()).await {
                            println!("Failed to write to stream: {}", error);
                        }
                    },
                }
            }
            Err(error) => {
                println!("Failed to read from stream: {}", error);
            }
        }

        // stream.shutdown().await.unwrap();
    }

    // pub async fn listen(&self, db: MySqlPool) {
    pub async fn listen(&self, db_url: String) {
        let listener = net::TcpListener::bind(format!("{}:{}", &self.host, &self.port)).await.expect("Failed to bind to address");

        println!("Server listening on {}:{}", &self.host, &self.port);

        loop {
            if let Ok(sock) = listener.accept().await {
                let pool = match MySqlPool::connect(&db_url)
                    .await {
                        Ok(pool) => pool,
                        Err(err) => {
                            println!("Failed to connect the database: {:?}", err);
                            std::process::exit(1);
                        }
                    };
                tokio::spawn(async move {
                    // function on test only!!
                    // let (cpu, ram, disk_read, disk_write) = benchmark_env_usage(Duration::from_secs(1));
                    // println!(
                    //     "Average CPU Usage: {:.2}%, RAM Usage: {:.2} Mb, Disk Read: {:.2} Mb, Disk Write: {:.2} Mb.", 
                    //     cpu, 
                    //     ram, 
                    //     disk_read, 
                    //     disk_write
                    // );
                    // time_function(|| Self::handle_client(sock.0, pool), "handle_client").await;
                    Self::handle_client(sock.0, pool).await;
                });
            } 
            // else {
            //     println!("Failed accepting connection!");
            // }
        }
    }
}
