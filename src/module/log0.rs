use sqlx::mysql::MySqlPool;

#[derive(Debug)]
pub struct LogHash {
    connection: MySqlPool,
    table: String,
    column: Vec<String>,
    content: Vec<String>,
}
impl LogHash {
    pub fn new(connection: MySqlPool, table: String, column: Vec<String>, content: Vec<String>) -> LogHash {
        LogHash { connection, table, column, content }
    }

    pub async fn build(&self) -> Result<String, Box<dyn std::error::Error>> {
        let set_str = self.column.iter().map(|_| "?").collect::<Vec<_>>().join(", ");
        let query = format!("INSERT INTO {} ({}) VALUES ({})", self.table, self.column.join(","), set_str);
        sqlx::query(&query)
            .bind(self.content[0].to_owned())
            .bind(self.content[1].to_owned())
            .bind(self.content[2].to_owned())
            .bind(self.content[3].to_owned())
            .bind(self.content[4].to_owned())
            .bind(self.content[5].to_owned())
            .bind(self.content[6].to_owned())
            .bind(self.content[7].to_owned())
            .execute(&self.connection)
            .await?;
        Ok("SUCCESS".to_string())
    }
}
