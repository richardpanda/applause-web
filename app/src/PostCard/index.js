import React, { Component } from "react";
import { Card, Icon, Image } from "semantic-ui-react";

import "./style.css";

class PostCard extends Component {
  render() {
    const { post } = this.props;

    return (
      <Card id="post-card">
        <a className="post-image-container" href={post.url} target="_blank">
          <Image src={post.img_url} id="post-image" centered />
        </a>
        <Card.Content textAlign="left">
          <a className="post-title" target="_blank" href={post.url}>
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
    );
  }
}

export default PostCard;
