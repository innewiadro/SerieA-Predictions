import pandas as pd

matches_data = pd.read_csv("matches_data.csv", index_col=0)
# print(matches_data)

matches_data["team"].value_counts()
# print(matches_data["team"].value_counts())

"""change data types"""
# print(matches_data.dtypes)
matches_data["date"] = pd.to_datetime(matches_data["date"])

"""venue code home/away  == 1/0"""
matches_data["venue_code"] = matches_data["venue"].astype("category").cat.codes

"""opponent code"""
matches_data["opp_code"] = matches_data["opponent"].astype("category").cat.codes

"""add hour column"""
matches_data["hour"] = matches_data["time"].str.replace(":.+", "", regex=True).astype("int")

"""add day code"""
matches_data["day_code"] = matches_data["date"].dt.dayofweek

"""change win, draw and lose to int => Win=1, draw or lose = 0"""
matches_data["target"] = (matches_data["result"] == "W").astype("int")

print(matches_data)

"""creating model"""
from sklearn.ensemble import RandomForestClassifier


rf = RandomForestClassifier(n_estimators=50, min_samples_split=10, random_state=1)

train = matches_data[matches_data["date"] < "2021-01-01"]
test = matches_data[matches_data["date"] > "2021-01-01"]

predictors = ["venue_code", "opp_code", "hour", "day_code"]

rf.fit(train[predictors], train["target"])


preds = rf.predict(test[predictors])

from sklearn.metrics import accuracy_score

acc = accuracy_score(test["target"], preds)
print(acc)


""""""
combined = pd.DataFrame(dict(actual=test["target"], prediction=preds))
print(pd.crosstab(index=combined["actual"], columns=combined["prediction"]))



from sklearn.metrics import precision_score
print(precision_score(test["target"], preds))


grouped_matches = matches_data.groupby("team")

group = grouped_matches.get_group("Milan")
print(group)


def rolling_averrages(group, cols, new_cols):
    group = group.sort_values("date")
    rolling_stats = group[cols].rolling(3, closed="left").mean()
    group[new_cols] = rolling_stats
    group = group.dropna(subset=new_cols)
    return group


cols = ["gf", "ga", "sh", "sot", "dist", "fk", "pk", "pkatt"]
new_cols = [f"{c}_rolling" for c in cols]
print(new_cols)

rolling_averrages(group, cols, new_cols)
matches_rolling = matches_data.groupby("team").apply(lambda x: rolling_averrages(x, cols, new_cols))
print(matches_rolling)

matches_rolling = matches_rolling.droplevel("team")
matches_rolling.index = range(matches_rolling.shape[0])

"""retrain"""""
print(matches_rolling["opponent"].value_counts())


def make_predictions(data, predictors):
    train = data[data["date"] < "2021-01-01"]
    test = data[data["date"] > "2021-01-01"]
    rf.fit(train[predictors], train["target"])
    preds = rf.predict(test[predictors])
    combined = pd.DataFrame(dict(actual=test["target"], predicted=preds), index=test.index)
    precision = precision_score(test["target"], preds)
    return combined, precision


combined, precision = make_predictions(matches_rolling, predictors + new_cols)

#print(combined, precision)

combined = combined.merge(matches_rolling[["date", "team","opponent", "result"]], left_index=True, right_index=True)

#print(combined)


class MissingDict(dict):
    __missing__ = lambda self, key: key


map_values = {"Internazionale": "Inter"}

mapping = MissingDict(**map_values)

combined["new_team"] = combined["team"].map(mapping)
print(combined)

merged = combined.merge(combined, left_on=["date", "new_team"], right_on=["date", "opponent"])

print(merged)

print(merged[(merged["predicted_x"] == 1) & (merged["predicted_y"] == 0)]["actual_x"].value_counts())

