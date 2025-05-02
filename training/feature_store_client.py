from feast import FeatureStore

store = FeatureStore(repo_path="feature_repo")

def get_features(transaction_id: str):
    return store.get_online_features(
        features=["transaction_features:amount_avg_1h"],
        entity_rows=[{"transaction": transaction_id}]
    ).to_dict()