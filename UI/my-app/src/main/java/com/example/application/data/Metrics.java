package com.example.application.data;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class Metrics {
    public  List<RequestsMetrics> Requests_metrics;
    public int Duration;
    public Map<String, Crash> Crashes;
    public Map<String, Hang> Hangs;
    public int episodes;
    private String id;

    public String getId() {
        return id;
    }

    public void setId(String id) {
        this.id = id;
    }

    public int getEpisodes() {
        return episodes;
    }

    public void setEpisodes(int episodes) {
        this.episodes = episodes;
    }

    public List<RequestsMetrics> getRequests_metrics() {
        return Requests_metrics;
    }

    public void setRequests_metrics(List<RequestsMetrics> requests_metrics) {
        Requests_metrics = requests_metrics;
    }

    public int getDuration() {
        return Duration;
    }

    public void setDuration(int duration) {
        Duration = duration;
    }

    public Map<String, Crash> getCrashes() {
        return Crashes;
    }

    public void setCrashes(Map<String, Crash> crashes) {
        Crashes = crashes;
    }

    public Map<String, Hang> getHangs() {
        return Hangs;
    }

    public void setHangs(Map<String, Hang> hangs) {
        Hangs = hangs;
    }



    public static class RequestLog {
        private int status_code;
        private String message;

        public int getStatus_code() {
            return status_code;
        }

        public void setStatus_code(int status_code) {
            this.status_code = status_code;
        }

        public String getMessage() {
            return message;
        }

        public void setMessage(String message) {
            this.message = message;
        }
    }

    public static class RequestsMetrics {
        private String name;
        private QTables q_tables;
        private List<Double> episode_rewards;
        private List<Double> state_visits;
        private Map<String, Map<String, Integer>> mutation_counts;
        private Map<String, Map<String, List<Double>>> mutation_rewards;
        private QValueConvergence q_value_convergence;

        // Getters and Setters
        public String getName() {
            return name;
        }

        public void setName(String name) {
            this.name = name;
        }

        public QTables getQ_tables() {
            return q_tables;
        }

        public void setQ_tables(QTables q_tables) {
            this.q_tables = q_tables;
        }

        public List<Double> getEpisode_rewards() {
            return episode_rewards;
        }

        public void setEpisode_rewards(List<Double> episode_rewards) {
            this.episode_rewards = episode_rewards;
        }

        public List<Double> getState_visits() {
            return state_visits;
        }

        public void setState_visits(List<Double> state_visits) {
            this.state_visits = state_visits;
        }

        public Map<String, Map<String, Integer>> getMutation_counts() {
            return mutation_counts;
        }

        public void setMutation_counts(Map<String, Map<String, Integer>> mutation_counts) {
            this.mutation_counts = mutation_counts;
        }

        public Map<String, Map<String, List<Double>>> getMutation_rewards() {
            return mutation_rewards;
        }

        public void setMutation_rewards(Map<String, Map<String, List<Double>>> mutation_rewards) {
            this.mutation_rewards = mutation_rewards;
        }

        public QValueConvergence getQ_value_convergence() {
            return q_value_convergence;
        }

        public void setQ_value_convergence(QValueConvergence q_value_convergence) {
            this.q_value_convergence = q_value_convergence;
        }

        public static class QTables {
            private List<List<Double>> int_q_table;
            private List<List<Double>> float_q_table;
            private List<List<Double>> bool_q_table;
            private List<List<Double>> byte_q_table;
            private List<List<Double>> string_q_table;

            // Getters and Setters
            public List<List<Double>> getInt_q_table() {
                return int_q_table;
            }

            public void setInt_q_table(List<List<Double>> int_q_table) {
                this.int_q_table = int_q_table;
            }

            public List<List<Double>> getFloat_q_table() {
                return float_q_table;
            }

            public void setFloat_q_table(List<List<Double>> float_q_table) {
                this.float_q_table = float_q_table;
            }

            public List<List<Double>> getBool_q_table() {
                return bool_q_table;
            }

            public void setBool_q_table(List<List<Double>> bool_q_table) {
                this.bool_q_table = bool_q_table;
            }

            public List<List<Double>> getByte_q_table() {
                return byte_q_table;
            }

            public void setByte_q_table(List<List<Double>> byte_q_table) {
                this.byte_q_table = byte_q_table;
            }

            public List<List<Double>> getString_q_table() {
                return string_q_table;
            }

            public void setString_q_table(List<List<Double>> string_q_table) {
                this.string_q_table = string_q_table;
            }
        }

        public static class QValueConvergence extends HashMap<String, Object> {
            public QValueConvergence() {
                // Default constructor
            }

            public List<List<List<Double>>> getQValues(String key) {
                return (List<List<List<Double>>>) get(key);
            }
        }
    }

    public static class Crash {
        private int count;
        private String error_message;
        private String stack_trace;
        private String sample_input;

        // Getters and setters

        public int getCount() {
            return count;
        }

        public void setCount(int count) {
            this.count = count;
        }

        public String getError_message() {
            return error_message;
        }

        public void setError_message(String error_message) {
            this.error_message = error_message;
        }

        public String getSample_input() {
            return sample_input;
        }

        public void setSample_input(String sample_input) {
            this.sample_input = sample_input;
        }

        public String getStack_trace() {
            return stack_trace;
        }

        public void setStack_trace(String stack_trace) {
            this.stack_trace = stack_trace;
        }
    }

    public static class Hang {
        private int count;
        private String error_message;
        private String url;
        private String method;
        private String parameters;

        // Getters and setters

        public int getCount() {
            return count;
        }

        public void setCount(int count) {
            this.count = count;
        }

        public String getError_message() {
            return error_message;
        }

        public void setError_message(String error_message) {
            this.error_message = error_message;
        }

        public String getUrl() {
            return url;
        }

        public void setUrl(String url) {
            this.url = url;
        }

        public String getMethod() {
            return method;
        }

        public void setMethod(String method) {
            this.method = method;
        }

        public String getParameters() {
            return parameters;
        }

        public void setParameters(String parameters) {
            this.parameters = parameters;
        }
    }
}

