import React, { Component } from "react";
import { Dropdown } from "semantic-ui-react";

class TopicDropdown extends Component {
  state = {
    topics: []
  };

  async componentDidMount() {
    const response = await fetch("/api/topics");
    const payload = await response.json();
    this.setState({ topics: payload.topics });
  }

  convertToTitle(topic) {
    return topic
      .split("-")
      .map(word => word[0].toUpperCase() + word.substring(1))
      .join(" ");
  }

  render() {
    const options = this.state.topics.map(topic => ({
      key: topic,
      value: topic,
      text: this.convertToTitle(topic)
    }));

    return (
      <Dropdown
        placeholder="Select a topic"
        search
        selection
        options={options}
        onChange={this.props.handleChange}
      />
    );
  }
}

export default TopicDropdown;
