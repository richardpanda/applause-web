import React, { Component } from "react";
import { Card, Grid, Icon, Image } from "semantic-ui-react";

import "./style.css";

class PostList extends Component {
  state = {
    posts: []
  };

  async componentWillUpdate(nextProps, _) {
    if (this.props.topic !== nextProps.topic) {
      const response = await fetch(`/api/topic/${nextProps.topic}/posts`);
      const payload = await response.json();
      this.setState({ posts: payload.posts });
    }
  }

  render() {
    return (
      <Grid id="post-list-container" centered>
        {this.state.posts.map(post => (
          <Grid.Row id="post-row" key={post.title}>
            <Card>
              <Image src={post.img_url} href={post.url} />
              <Card.Content textAlign="left">
                <a className="post-title" href={post.url}>
                  {post.title}
                </a>
                <div className="post-creator">{post.creator}</div>
              </Card.Content>
              <Card.Content extra textAlign="left">
                <div className="post-likes">
                  <Icon name="thumbs outline up" />
                  {post.total_clap_count} Likes
                </div>
              </Card.Content>
            </Card>
          </Grid.Row>
        ))}
      </Grid>
    );
  }
}

export default PostList;
