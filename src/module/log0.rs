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

    pub async fn build(&mut self) -> Result<String, Box<dyn std::error::Error>> {
        let name = self.content.remove(0);
        let values = self.content.iter().map(|s| format!("\"{}\"", s)).collect::<Vec<String>>().join(",");
        let query = format!("INSERT INTO {} ({}) VALUES ({})", self.table, self.column.join(","), values);
        sqlx::query(&query)
            .execute(&self.connection)
            .await?;
        Ok(name)
    }
}
