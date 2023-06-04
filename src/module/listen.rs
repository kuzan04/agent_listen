use tokio::io::{AsyncReadExt, AsyncWriteExt};
use tokio::net;
use sqlx::{MySqlPool, FromRow};

use crate::module::log0::LogHash;
use crate::module::file::FileDirectory;
use crate::module::db::{TestConnect, DatabaseCheck};

use crate::model::{AgentStore, AgentManage, AgentHistory};

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
            Ok(t) => { match t {
                    1 => {
                        if let Ok(res) = TestConnect::new(host, user, passwd, database).mysql().await {
                            success = res
                        } else {
                            success = "Query details table error.".to_string()
                        }
                    },
                    0 => {
                        if let Ok(res) = TestConnect::new(host, user, passwd, database).oracle().await {
                            success = res
                        } else {
                            success = "Query details table error.".to_string()
                        }
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
        if selected.agm_id == -1 && selected.agm_name == *"unknow".to_string() && selected.code == *"unknow".to_string() {
            Err("Not Found".to_string())
        } else{
            Ok(selected)
        }
    }

    async fn set_history(db: MySqlPool, manager: Vec<AgentManage>, code: String, name: String) -> String {
        let env_history = Self::split_string(&dotenv::var("TB_HISTORY").unwrap_or_else(|_| "TB_TR_PDPA_AGENT_LISTEN_HISTORY:agm_id".to_string()), ":");
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
        match selected {
            Ok(agm) => {
                let mut message = String::new();
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
                    _ => "Success".to_string(),
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
                        // Convert message from_client and values
                        let from_client = content.remove(0);

                        DatabaseCheck::new(db, from_client, dbc_table, dbc_columns, content);

                        details[1].to_string()
                    },
                    _ => {
                        "Failed".to_string()
                    }
                }
            },
            false => "Close".to_string()
        }
    }

    async fn handle_client(mut stream: net::TcpStream, db: MySqlPool) {
        let mut buffer = [0; 1024];
        match stream.read(&mut buffer).await {
            Ok(bytes_read) => {
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
                        println!("{}", result);
                        // Set message to response client.
                        // message = Self::set_history(db.clone(), manager, response[0].to_owned(), result).await;
                        message = "Test".to_string();
                        if let Err(error) = stream.write_all(message.as_bytes()).await {
                            println!("Failed to write to stream: {}", error);
                        }
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

        stream.shutdown().await.unwrap();
    }

    pub async fn listen(&self, db: MySqlPool) {
        let listener = net::TcpListener::bind(format!("{}:{}", &self.host, &self.port)).await.expect("Failed to bind to address");

        println!("Server listening on {}:{}", &self.host, &self.port);

        loop {
            if let Ok(sock) = listener.accept().await{
                let cloned_db = db.clone();
                tokio::spawn(async move {
                    Self::handle_client(sock.0, cloned_db).await;
                });
            } else {
                println!("Failed accepting connection!");
            }
        }
    }
}
