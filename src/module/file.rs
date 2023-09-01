use sqlx::{mysql::{MySqlPool, MySqlRow}, Row};
use std::fs::{read_dir, ReadDir, rename};
use std::path::Path;

//use on test
// use crate::module::test::*;

#[derive(Debug)]
#[allow(dead_code)]
pub struct FileDirectory {
    connection: MySqlPool,
    table: String,
    column: Vec<String>,
    directory: String,
    log_path: String,
    doc_path: String,
    content: Vec<String>
}

impl FileDirectory {
    pub fn new(connection: MySqlPool, table: String, column: Vec<String>, directory: String, log_path: String, doc_path: String, content: Vec<String>) -> FileDirectory {
        FileDirectory { connection, table, column, directory, log_path, doc_path, content }
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

    fn find_match(arr: Vec<Vec<String>>, val: Vec<String>) -> bool {
        let mut result = false;
        for i in arr {
            let mut equal_result = i[1..].iter().zip(val.iter()).map(|(a, b)| a == b).collect::<Vec<bool>>();
            equal_result.retain(|&value| value);
            if equal_result.len() > 3 {
                result = true;
            }
        }
        result
    }

    #[allow(clippy::needless_collect)]
    fn reverse_name(files: ReadDir, name: String) -> bool {
        let mut result = false;
        for i in files {
            let filename: Vec<String> =  i.unwrap()
                .file_name()
                .to_string_lossy()
                .split('@')
                .map(|s| s.to_string())
                .collect();
            if filename.contains(&name) {
                result = true;
            }
        }
        result
    }

    pub async fn build(&mut self) -> Result<String, Box<dyn std::error::Error>> {
        let name = self.content.remove(0);
        let query_dir: Vec<Vec<String>> = sqlx::query(
            format!(
                "SELECT {} FROM {} ORDER BY {} ASC;",
                self.column.join(", "),
                self.table,
                self.column[0]
            ).as_str()
        )
            .fetch_all(&self.connection)
            .await.unwrap()
            .into_iter()
            .map(|row| {
                Self::set_query(self.column.clone(), &row)
                // function on test only!!
                // time_function(|| Self::set_query(self.column.clone(), &row), "file_set_query")
            })
            .collect();
        let values = self.content.clone().iter().map(|s| format!("\"{}\"", s)).collect::<Vec<String>>().join(", ");
        let files = read_dir(&self.directory).expect("Failed to read directory!");
        // Check result query dir/file == [] and if result query dir/file > 0
        // and check result == value if true = false , false = true
        if query_dir.is_empty() || !Self::find_match(query_dir, self.content.clone()) {
        // function on test only!!
        // if query_dir.is_empty() || time_function(|| !Self::find_match(query_dir, self.content.clone()), "file_find_match") {
            sqlx::query(format!("INSERT INTO {} ({}) VALUES ({})", self.table, &self.column[1..].join(", "), values).as_str())
                .fetch_all(&self.connection)
                .await.unwrap();
        } else if Self::reverse_name(files, self.content[self.content.len() - 2].to_string()) {
        // } else if time_function(|| Self::reverse_name(files, self.content[self.content.len() - 2].to_string()), "file_reverse_name") {
            sqlx::query(
                format!("UPDATE {} SET {} = {}, _get = NOW() WHERE {} = \"{}\"",
                    self.table,
                    self.column[self.column.len() - 1],
                    self.content[self.content.len() - 1],
                    self.column[self.column.len() - 2],
                    self.content[self.content.len() - 2]
                ).as_str()
            )
                .execute(&self.connection)
                .await.unwrap();
        } 
        self.move_dir().await;
        // time_function(|| self.move_dir(), "move_dir").await;
        Ok(name)
    }

    async fn move_dir(&mut self) {
        let files = read_dir(&self.directory).expect("Failed to read directory!");
        let source_path = match self.directory.chars().nth(self.directory.len() - 1).unwrap() {
            '/' => self.directory.clone(),
            _ => format!("{}/", self.directory),
        };
        for i in files {
            let filename: Vec<String> = i.unwrap().file_name().to_string_lossy()
                .split('@')
                .map(|s| s.to_string())
                .collect();
            if let Some(extension) = Path::new(format!("{}{}", source_path, filename.join("@")).as_str()).extension() {
                if let Some(extension_str) = extension.to_str() {
                    if filename[filename.len() - 1] != ".DS_Store" && extension_str == "log" {
                        let destination_path = match self.log_path.chars().nth(self.log_path.len() - 1).unwrap() {
                            '/' => self.log_path.clone(),
                            _ => format!("{}/", self.log_path),
                        };
                        rename(
                            format!("{}{}", source_path, filename.join("@")).as_str(),
                            format!("{}{}", destination_path, filename.join("@")).as_str()
                        ).unwrap();
                    } else if filename[filename.len() - 1] != ".DS_Store" && vec!["csv", "xlsx", "xls"].contains(&extension_str) {
                        let destination_path = match self.doc_path.chars().nth(self.doc_path.len() - 1).unwrap() {
                            '/' => self.doc_path.clone(),
                            _ => format!("{}/", self.doc_path),
                        };
                        rename(
                            format!("{}{}", source_path, filename.join("@")).as_str(),
                            format!("{}{}", destination_path, filename.join("@")).as_str()
                        ).unwrap();
                    } 
                }
            }
        }
    }
}
