use sqlx::{mysql::{MySqlPool, MySqlRow}, Row};
use std::path::Path;
// use std::fs::File;

#[derive(Debug)]
#[allow(dead_code)]
pub struct FileDirectory {
    connection: MySqlPool,
    table: String,
    column: Vec<String>,
    directory: Box<Path>,
    log_path: Box<Path>,
    doc_path: Box<Path>,
    content: Vec<String>
}

impl FileDirectory {
    pub fn new(connection: MySqlPool, table: String, column: Vec<String>, directory: &Path, log_path: &Path, doc_path: &Path, content: Vec<String>) -> FileDirectory {
        let dir = directory.into();
        let lpath = log_path.into();
        let dpath = doc_path.into();
        FileDirectory { connection, table, column, directory: dir, log_path: lpath, doc_path: dpath, content }
    }

    fn set_query(column: Vec<String>, query: &MySqlRow) -> Vec<String> {
        let mut result = Vec::new();
        for i in column {
            let value: Result<Option<String>, sqlx::Error> = query.try_get(i.trim());
            match value {
                Ok(Some(val)) => result.push(val),
                Ok(None) => result.push("NULL".to_string()),
                Err(e) => {
                    let err: Vec<String> = e.to_string().split('`').into_iter().map(|s| s.to_string()).collect();
                    match err[err.len() - 2].as_str() {
                        "INT" => {
                            let new_value: i32 = query.get(i.trim());
                            result.push(new_value.to_string())
                        },
                        _ => result.push("Unknow".to_string()),
                    }
                },
            }
        }
        result
    }

    pub async fn build(&self) {
        let query_dir: Vec<Vec<String>> = sqlx::query(format!("SELECT {} FROM {} ORDER BY {} ASC;", self.column.join(", "), self.table, self.column[0]).as_str())
            .fetch_all(&self.connection)
            .await.unwrap()
            .into_iter()
            .map(|row| {
                Self::set_query(self.column.clone(), &row)
            })
            .collect();
        println!("{:#?}", query_dir);
        // Ok("Hello from server!".to_string())
    }
}
