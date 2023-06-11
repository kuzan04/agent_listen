install:
	cargo add dotenv@0.15.0
	cargo add tokio@1.28.2 -F "full"
	cargo add rcgen@0.10.0
	cargo add get_if_addrs@0.5.3
	cargo add chrono@0.4.24 -F "serde"
	cargo add serde@1.0.163 -F "derive"
	cargo add serde_json@1.0.96
	cargo add oracle@0.5.7 -F "chrono stmt_without_lifetime aq_unstable"
	cargo add sqlx@0.6.3 -F "runtime-async-std-native-tls mysql chrono"
	cargo install cargo-watch@8.4.0

run:
	cargo-watch -q -c -w src/ -x run
